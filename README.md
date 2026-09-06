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
7. **`nxf-shiny`** (Port: `3807`), run various Nextflow apps, use `-profile singularity` 

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
wget https://raw.githubusercontent.com/angelovangel/tgs-lab-apps/refs/heads/main/docker-compose.yml

# to start all apps
docker compose -f up -d
# to start a specific app only (e.g. rapid-barcoding-ont)
docker compose up -d rapid-barcoding-ont
# to stop
docker compose down
```
You need to allow access to ports `3801`to`3806` on your server firewall.
```bash
sudo ufw allow 3801:3806/tcp
sudo ufw reload
sudo ufw status
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