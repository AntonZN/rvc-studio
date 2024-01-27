from django.db import models


class Status(models.TextChoices):
    DONE = "done"
    ERROR = "error"
    PENDING = "pending"
    DELETED = "deleted"


class Record(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField("Название", max_length=256)
    file_path = models.TextField()
    status = models.CharField(choices=Status, default=Status.PENDING, max_length=100)
    vocal_path = models.TextField(null=True, blank=True)
    instrumental_path = models.TextField(null=True, blank=True)
    clone_path = models.TextField(null=True, blank=True)
    cover_path = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TTS(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.CharField(choices=Status, default=Status.PENDING, max_length=100)
    voice_path = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
