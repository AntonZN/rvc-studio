from enum import Enum

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Status(str, Enum):
    DONE = "done"
    ERROR = "error"
    PENDING = "pending"
    DELETED = "deleted"


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


class TTS(Model):
    id = fields.UUIDField(pk=True)
    status = fields.CharField(choices=Status, default=Status.PENDING, max_length=100)
    voice_path = fields.TextField(null=True, blank=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "studio_tts"


TTSSchema = pydantic_model_creator(
    TTS,
    name="TTSSchema",
)
RecordSchema = pydantic_model_creator(
    Record,
    name="RecordSchema",
    exclude=(
        "file_path",
        "vocal_path",
        "instrumental_path",
        "clone_path",
        "cover_path",
    ),
)

RecordStatusSchema = pydantic_model_creator(
    Record,
    name="RecordStatusSchema",
    exclude=("file_path", "name"),
)
