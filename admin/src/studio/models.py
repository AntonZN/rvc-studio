from django.db import models


class Status(models.TextChoices):
    DONE = "done", "done"
    ERROR = "error", "error"
    PENDING = "pending", "pending"
    PROCESSING = "processing", "processing"
    DELETED = "deleted", "deleted"
    CANCELED = "canceled", "canceled"


class Record(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField("Название", max_length=256)
    file_path = models.TextField()
    status = models.CharField(
        choices=Status.choices, default=Status.PENDING, max_length=100
    )
    vocal_path = models.TextField(null=True, blank=True)
    instrumental_path = models.TextField(null=True, blank=True)
    clone_path = models.TextField(null=True, blank=True)
    cover_path = models.TextField(null=True, blank=True)
    denoised_path = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TTS(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.CharField(
        choices=Status.choices, default=Status.PENDING, max_length=100
    )
    voice_path = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProcessRequest(models.Model):
    process_type = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    waiting_time_in_seconds = models.IntegerField()


class Statistics(models.Model):
    date = models.DateField()
    count_cover = models.IntegerField()
    count_tts = models.IntegerField()
    count_split = models.IntegerField()
    count_split_old = models.IntegerField()
    count_clone = models.IntegerField()
    count_denoise = models.IntegerField(null=True, blank=True)
    average_waiting = models.CharField(max_length=256)

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
