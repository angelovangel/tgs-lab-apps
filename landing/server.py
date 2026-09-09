#!/usr/bin/env python3
import os
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import time

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8088"))
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "15"))


def update_status_loop():
    while True:
        time.sleep(REFRESH_SECONDS)
        try:
            subprocess.run([sys.executable, str(ROOT / "render_page.py")], check=False, cwd=str(ROOT))
        except Exception as e:
            print(f"Error updating status: {e}", file=sys.stderr)


class LandingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)


if __name__ == "__main__":
    # Pre-render the landing page once at startup
    try:
        subprocess.run([sys.executable, str(ROOT / "render_page.py")], check=False, cwd=str(ROOT))
    except Exception as e:
        print(f"Initial render failed: {e}", file=sys.stderr)

    # Start background thread to update status periodically
    updater_thread = threading.Thread(target=update_status_loop, daemon=True)
    updater_thread.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), LandingHandler)
    print(f"Serving landing page statically on http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
