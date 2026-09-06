# TGS Lab Apps Setup

Containerized deployment setup for Opentrons automation and Nextflow minimapper Shiny dashboards.

---

## 📦 Included Services

| Service | Port | Notes |
| --- | ---: | --- |
| `rapid-barcoding-ont` | `3801` | Setup ONT rapid barcoding on Opentrons OT-2 |
| `custom-transfer-opentrons` | `3802` | One step transfer setup on OT-2 and Flex |
| `kinnex-ot2` | `3803` | Setup Kinnex PCR on Opentrons OT-2 |
| `sanger-opentrons` | `3804` | Setup Sanger reactions on Opentrons OT-2 |
| `tracer` | `3805` | Sanger files QC |
| `nxf-minimapper` | `3806` | `minimapper-app`; uses Singularity by default |
| `nxf-shiny` | `3807` | Run various Nextflow apps; use `-profile singularity`; server needs a `/mnt` path |

---

## 🚀 How to Run Locally

```bash
cd tgs-lab-apps

# Start one of the services
docker compose up -d rapid-barcoding-ont
```
Access the app by going to `http://localhost:3801`.

```bash
cd tgs-lab-apps

# start all services
docker compose up -d
```
Access apps by going to `http://localhost:[PORT]`

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