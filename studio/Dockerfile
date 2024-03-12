FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

RUN apt-get update && \
    apt-get install -y python3.10 python3-pip python3.10-dev ffmpeg libsndfile1 wget tar espeak && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt


RUN pip install --upgrade pip

COPY . /app

CMD ["python", "run.py"]