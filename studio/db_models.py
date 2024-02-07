from enum import Enum

from tortoise import fields
from tortoise.models import Model


class Status(str, Enum):
    DONE = "done"
    ERROR = "error"
    PENDING = "pending"
    PROCESSING = "processing"
    DELETED = "deleted"
    CANCELED = "canceled"


class Record(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=256)
    file_path = fields.TextField()
    status = fields.CharField(choices=Status, default=Status.PENDING, max_length=100)
    vocal_path = fields.TextField(null=True, blank=True)
    instrumental_path = fields.TextField(null=True, blank=True)
    clone_path = fields.TextField(null=True, blank=True)
    cover_path = fields.TextField(null=True, blank=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "studio_record"


class RVCModel(Model):
    id = fields.IntField(pk=True)
    ru = fields.CharField(max_length=256, null=True)
    en = fields.CharField(max_length=256, null=True)
    es = fields.CharField(max_length=256, null=True)
    pt = fields.CharField(max_length=256, null=True)
    fr = fields.CharField(max_length=256, null=True)
    hi = fields.CharField(max_length=256, null=True)
    ko = fields.CharField(max_length=256, null=True)
    description = fields.TextField(null=True)
    lock = fields.BooleanField(default=False)
    hide = fields.BooleanField(default=False)
    image = fields.TextField(null=True)
    file = fields.TextField()

    class Meta:
        table = "rvc_rvcmodel"


class TTS(Model):
    id = fields.UUIDField(pk=True)
    status = fields.CharField(choices=Status, default=Status.PENDING, max_length=100)
    voice_path = fields.TextField(null=True, blank=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "studio_tts"
