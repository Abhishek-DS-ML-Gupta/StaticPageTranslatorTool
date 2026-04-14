FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install fastapi uvicorn python-multipart sentencepiece && \
    pip install transformers==4.45.0 && \
    pip install git+https://github.com/VarunGumma/IndicTransToolkit.git

EXPOSE 8080

# Cloud Run injects the PORT environment variable. Default to 8080 if not found.
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
