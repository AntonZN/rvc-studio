FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /admin

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /admin

ENV DJANGO_SETTINGS_MODULE=src.settings

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]