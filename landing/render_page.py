#!/usr/bin/env python3
import json
import os
import re
import socket
import subprocess
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
SERVICES_PATH = ROOT / "services.json"
HTML_PATH = ROOT / "index.html"
COMPOSE_FILE = ROOT.parent / "docker-compose.yml"
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "15"))


def _is_docker_alias(ip: str) -> bool:
    value = (ip or "").strip().lower()
    if not value:
        return True
    invalid_values = {
        "localhost",
        "127.0.0.1",
        "::1",
        "host.docker.internal",
        "gateway.docker.internal",
        "host-gateway",
    }
    if value in invalid_values or value.startswith("host.docker.internal") or value.startswith("gateway.docker.internal"):
        return True

    if value.startswith("169.254."):
        return True

    if value.startswith("10."):
        return True

    if value.startswith("172."):
        try:
            second_octet = int(value.split(".", 2)[1])
            return 17 <= second_octet <= 31
        except ValueError:
            return False

    return False


def detect_server_ip() -> str:
    env_ip = os.environ.get("SERVER_IP")
    if env_ip:
        candidate = env_ip.strip()
        if candidate and not _is_docker_alias(candidate):
            return candidate

    try:
        result = subprocess.check_output(["hostname", "-I"], text=True, stderr=subprocess.DEVNULL)
        ips = [part.strip() for part in result.split() if part.strip()]
        for ip in ips:
            if ip and not _is_docker_alias(ip):
                return ip
    except Exception:
        pass

    try:
        hostname_ip = socket.gethostbyname(socket.gethostname())
        if hostname_ip and not _is_docker_alias(hostname_ip):
            return hostname_ip
    except Exception:
        pass

    try:
        public_ip = urlopen("https://api.ipify.org", timeout=5).read().decode("utf-8").strip()
        if public_ip:
            return public_ip
    except Exception:
        pass

    return "127.0.0.1"


def get_compose_project_name() -> str:
    try:
        compose_text = COMPOSE_FILE.read_text()
    except Exception:
        return "tgs-lab-apps"

    match = re.search(r"^\s*name:\s*['\"]?([^'\"\n]+)", compose_text, re.M)
    return match.group(1).strip() if match else "tgs-lab-apps"


def get_compose_status_map() -> dict[str, str]:
    status_map: dict[str, str] = {}
    project_name = get_compose_project_name()

    try:
        result = subprocess.check_output(
            ["docker", "compose", "-f", str(COMPOSE_FILE), "ps", "--all", "--format", "json"],
            cwd=str(ROOT.parent),
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        result = ""

    raw_items = []
    if result.strip():
        try:
            parsed = json.loads(result)
            if isinstance(parsed, list):
                raw_items = parsed
            elif isinstance(parsed, dict):
                raw_items = [parsed]
        except json.JSONDecodeError:
            raw_items = []

    if not raw_items:
        for line in result.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                raw_items.append(payload)

    if not raw_items:
        try:
            fallback = subprocess.check_output(
                [
                    "docker",
                    "ps",
                    "-a",
                    "--filter",
                    f"label=com.docker.compose.project={project_name}",
                    "--format",
                    "{{.Label \"com.docker.compose.service\"}}|{{.State}}",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            fallback = ""

        for line in fallback.splitlines():
            line = line.strip()
            if not line or "|" not in line:
                continue
            service_name, state = line.split("|", 1)
            if service_name.strip():
                status_map[service_name.strip()] = state.strip()
        return status_map

    for item in raw_items:
        if not isinstance(item, dict):
            continue
        name = item.get("Service") or item.get("Name")
        state = item.get("Status") or item.get("State") or ""
        if not name:
            continue
        status_map[str(name)] = str(state)

    return status_map


def status_label(raw_status: str) -> str:
    status = (raw_status or "").strip()
    if not status:
        return "Not started"

    normalized = status.lower()
    if normalized == "running" or normalized.startswith("up "):
        return "Running"
    if normalized.startswith("restarting"):
        return "Restarting"
    if normalized in {"created", "exited", "dead", "paused"} or normalized.startswith("exited"):
        return "Stopped"
    return status.title()


def render_html(services, server_ip: str, status_map: dict[str, str]) -> str:
    rows = []
    for svc in services:
        name = svc["name"]
        port = svc["port"]
        notes = svc["notes"]
        url = f"http://{server_ip}:{port}"
        raw_status = status_map.get(name, "")
        label = status_label(raw_status)
        if label == "Running":
            color = "#198754"
        elif label == "Restarting":
            color = "#fd7e14"
        elif label == "Stopped":
            color = "#dc3545"
        else:
            color = "#6c757d"
        badge_text = raw_status or "Not started"
        rows.append(
            """
            <tr>
              <td>{name}</td>
              <td><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></td>
              <td>{notes}</td>
              <td><span style="display:inline-block;padding:4px 8px;border-radius:999px;background-color:{color};color:white;font-weight:bold;">{badge_text}</span></td>
            </tr>
            """.format(name=name, url=url, notes=notes, color=color, badge_text=badge_text)
        )

    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>TGS Lab Apps</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        margin: 40px;
        background: #f8f9fa;
      }}
      h1 {{
        margin-bottom: 20px;
      }}
      table {{
        width: 100%;
        max-width: 1100px;
        border-collapse: collapse;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      }}
      th, td {{
        padding: 12px 14px;
        border: 1px solid #ddd;
        text-align: left;
        vertical-align: top;
      }}
      th {{
        background: #0d6efd;
        color: white;
      }}
      a {{
        color: #0d6efd;
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
      .meta {{
        margin-bottom: 18px;
        color: #555;
        font-size: 14px;
      }}
    </style>
    <meta http-equiv="refresh" content="{REFRESH_SECONDS}" />
    <script>
      setTimeout(function() {{
        window.location.reload();
      }}, {REFRESH_SECONDS * 1000});
    </script>
  </head>
  <body>
    <h1>TGS Lab Apps</h1>
    <div class="meta">Auto-refreshing every {REFRESH_SECONDS} seconds</div>
    <table>
      <thead>
        <tr>
          <th>Service</th>
          <th>URL</th>
          <th>Notes</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </body>
</html>
"""


def main() -> None:
    services = json.loads(SERVICES_PATH.read_text())
    server_ip = detect_server_ip()
    status_map = get_compose_status_map()
    HTML_PATH.write_text(render_html(services, server_ip, status_map))
    print(f"Rendered landing page for {server_ip} with {len(status_map)} docker statuses")


if __name__ == "__main__":
    main()
