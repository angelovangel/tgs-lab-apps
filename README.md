# TGS Lab Apps Setup

Containerized deployment setup for Opentrons automation and Nextflow minimapper Shiny dashboards.

---

## 📦 Included Services

1. **`rapid-barcoding-ont`** (Port: `3801`)
2. **`custom-transfer-opentrons`** (Port: `3802`)
3. **`kinnex-ot2`** (Port: `3803`)
4. **`sanger-opentrons`** (Port: `3804`)
5. **`tracer`** (Port: `3805`)
6. **`nxf-minimapper`** (`minimapper-app`, Port: `3806`, uses Singularity by default)

---

## 🚀 How to Run Locally

```bash
cd tgs-opentrons-apps

# Build images and start services
docker compose up -d --build
```
Access apps by going to `http://localhost:[PORT]`.

---

## 🖥 Remote Server Deployment

Only docker with docker compose plugin is needed on the server
```bash
curl -sSl https://raw.githubusercontent.com/angelovangel/tgs-lab-apps/refs/heads/main/docker-compose.yml | docker compose -f - up -d
```

Or, first transfer the `docker-compose.yml` file in a folder on your remote server and run the following commands:

```bash
cd your_folder
docker compose pull
docker compose up -d
# to stop
docker compose down
```

Access apps by going to `http://[SERVER_IP]:[PORT]`. Check status with `docker compose ps` and `docker compose stats`

## 📤 Development - Build & Push to Docker Hub

```bash
cd tgs-opentrons-apps

# Build and push all apps
./build_and_push.sh aangeloo latest

# Build and push specific app(s) only (3rd positional argument)
./build_and_push.sh aangeloo latest rapid-barcoding-ont,kinnex-ot2
```

---