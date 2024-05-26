FROM python:3.8

RUN apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN pip install numpy
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]