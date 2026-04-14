# 🚀 Static Page Translator Tool (Full Production Setup)

GPU-powered **Indic Translation API** using FastAPI + Docker + Cloudflare Tunnel with persistent background execution via `tmux`.

---

# 📌 Features

* ⚡ Fast GPU-based translation (IndicTrans2)
* 🌐 Public API (free via Cloudflare Tunnel)
* 🐳 Dockerized deployment
* 🔁 Persistent execution using `tmux`
* 🧠 Supports multiple Indic languages
* 🔌 Chrome extension ready (content.js)

---

# 🧱 Project Structure

```id="psu1u0"
StaticPageTranslatorTool/
├── app.py
├── requirements.txt
├── Dockerfile
├── index.html
├── content.js
├── manifest.json
└── README.md
```

---

# ⚙️ Requirements

* Linux (Ubuntu recommended)
* NVIDIA GPU (A6000 / 4090 / T4)
* Docker
* NVIDIA Container Toolkit
* Git

---

# 📥 Step 1 — Clone Repository

```bash id="m9p9nq"
git clone https://github.com/Abhishek-DS-ML-Gupta/StaticPageTranslatorTool.git
cd StaticPageTranslatorTool
```

---

# 🐳 Step 2 — Install Docker + GPU Support

```bash id="y1q8d9"
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker

# NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add - \
&& curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

---

# 📦 Step 3 — requirements.txt

```id="hp7cmy"
fastapi
uvicorn
torch
transformers
sentencepiece
IndicTransToolkit
```

---

# 🐳 Step 4 — Dockerfile

```dockerfile id="j3ns6o"
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

# 🏗️ Step 5 — Build Docker Image

```bash id="x2f5wh"
docker build -t bharatgen-api .
```

---

# ▶️ Step 6 — Run Container (Detached + GPU)

```bash id="h1zv9k"
docker run -d \
  --gpus all \
  -p 8001:8080 \
  --restart unless-stopped \
  --name bharatgen-container \
  bharatgen-api
```

---

# 🔍 Step 7 — Verify API

```bash id="84u9sy"
curl http://localhost:8001/languages
```

---

# 🌐 Step 8 — Install Cloudflare Tunnel

```bash id="x1g8fq"
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
```

---

# 🧵 Step 9 — Run Tunnel using tmux (IMPORTANT)

## Start tmux session

```bash id="0h3kjg"
tmux new -s tunnel
```

## Run Cloudflare tunnel

```bash id="7pspyo"
./cloudflared tunnel --url http://localhost:8001 --protocol http2
```

---

# 🔓 Step 10 — Get Public URL

You will see:

```id="3qqlfy"
https://xxxxx.trycloudflare.com
```

---

# 🔁 Step 11 — Keep Running (Detach tmux)

Press:

```id="xqv2j9"
CTRL + B → D
```

---

# 🔗 Step 12 — Test Public API

```bash id="d2rz4p"
curl https://xxxxx.trycloudflare.com/languages
```

---

# 🔄 Step 13 — Reattach tmux

```bash id="n2dl6o"
tmux attach -t tunnel
```

---

## 📸 Screenshots

<p align="center">
  <img src="assets/english.jpg" width="800"/>
</p>

<p align="center">
  <img src="assets/hindi.jpg" width="800"/>
</p>

---

# 🛠️ Docker Management

```bash id="v6qk4p"
docker ps
docker logs -f bharatgen-container
docker restart bharatgen-container
docker stop bharatgen-container
docker rm -f bharatgen-container
```

---

# 🌍 API Usage

## Translate

```bash id="tq3w0q"
curl -X POST http://localhost:8001/translate \
  -F "sentences=Hello world" \
  -F "src_lang=eng_Latn" \
  -F "tgt_lang=hin_Deva"
```

---

## Languages

```bash id="0i3b1k"
curl http://localhost:8001/languages
```

---

# ⚠️ Notes

* Cloudflare quick tunnel URL changes on restart
* Keep tmux session running to maintain uptime
* GPU required for optimal performance

---

# 🧠 Architecture

```id="o7i1lz"
Client (Browser / Extension)
        ↓
Cloudflare Tunnel
        ↓
Docker Container (GPU)
        ↓
FastAPI (IndicTrans)
```

---

# 🔥 Future Improvements

* API key authentication
* Rate limiting
* Custom domain (Cloudflare)
* React frontend dashboard
* SaaS monetization

---

# ✅ Status

* ✅ GPU enabled
* ✅ Dockerized
* ✅ Public API available
* ✅ Persistent using tmux
* ✅ Production ready (free setup)

---
