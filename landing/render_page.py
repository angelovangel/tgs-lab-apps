#!/usr/bin/env python3
import json
import os
import socket
import subprocess
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
SERVICES_PATH = ROOT / "services.json"
HTML_PATH = ROOT / "index.html"
COMPOSE_FILE = ROOT.parent / "docker-compose.yml"
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "15"))


def detect_server_ip() -> str:
    env_ip = os.environ.get("SERVER_IP")
    if env_ip and env_ip.strip() not in ("", "localhost"):
        return env_ip.strip()

    try:
        result = subprocess.check_output(["hostname", "-I"], text=True, stderr=subprocess.DEVNULL)
        ips = [part.strip() for part in result.split() if part.strip()]
        for ip in ips:
            if ip and ip != "127.0.0.1":
                return ip
    except Exception:
        pass

    try:
        hostname_ip = socket.gethostbyname(socket.gethostname())
        if hostname_ip and hostname_ip != "127.0.0.1":
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


def get_compose_status_map() -> dict[str, str]:
    status_map: dict[str, str] = {}

    try:
        result = subprocess.check_output(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "label=com.docker.compose.project=tgs-opentrons-apps",
                "--format",
                "{{.Label \"com.docker.compose.service\"}}|{{.State}}",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return status_map

    for line in result.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        service_name, state = line.split("|", 1)
        service_name = service_name.strip()
        state = state.strip()
        if service_name:
            status_map[service_name] = state

    return status_map


def status_label(raw_status: str) -> str:
    status = (raw_status or "").strip().lower()
    if not status:
        return "Not started"
    if "running" in status or status.startswith("up"):
        return "Running"
    if "restarting" in status:
        return "Restarting"
    if "exited" in status or status.startswith("exited") or "created" in status:
        return "Stopped"
    return "Not started"


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
        rows.append(
            """
            <tr>
              <td>{name}</td>
              <td><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></td>
              <td>{notes}</td>
              <td><span style="display:inline-block;padding:4px 8px;border-radius:999px;background-color:{color};color:white;font-weight:bold;">{label}</span></td>
            </tr>
            """.format(name=name, url=url, notes=notes, color=color, label=label)
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
