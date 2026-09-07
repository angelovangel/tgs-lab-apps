#!/usr/bin/env python3
import os
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "80"))
LOCK = threading.Lock()


class LandingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with LOCK:
                subprocess.run([sys.executable, str(ROOT / "render_page.py")], check=False, cwd=str(ROOT))
        return super().do_GET()


if __name__ == "__main__":
    # Pre-render the landing page once at startup to avoid initial 404s
    try:
        subprocess.run([sys.executable, str(ROOT / "render_page.py")], check=False, cwd=str(ROOT))
    except Exception:
        pass

    server = ThreadingHTTPServer(("0.0.0.0", PORT), LandingHandler)
    print(f"Serving landing page on http://0.0.0.0:{PORT}")
    server.serve_forever()
