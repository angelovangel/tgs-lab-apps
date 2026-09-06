# Landing Page

This folder renders a tiny static landing page with links to each app in the stack.

## How it works

- `services.json` is the single source of truth for service names, ports, and notes.
- `render_page.py` reads that file and automatically detects the server IP.
- It writes `index.html` with a table of URLs such as `http://SERVER_IP:3801`.

## Run locally

```bash
cd landing
SERVER_IP=$(hostname -I | awk '{print $1}') python render_page.py
python -m http.server 80
```

Then open:

```text
http://localhost/
```

## Run via Docker Compose

Add this service to the main compose file:

```yaml
  landing:
    image: python:3.12-alpine
    working_dir: /app
    volumes:
      - ./landing:/app
    environment:
      SERVER_IP: ${SERVER_IP}
    command: >
      sh -c "python render_page.py && python -m http.server 80 --directory /app"
    ports:
      - "80:80"
```

Then start it with:

```bash
export SERVER_IP=$(hostname -I | awk '{print $1}')
docker compose up -d landing
```
