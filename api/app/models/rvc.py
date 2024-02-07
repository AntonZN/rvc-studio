from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


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
    order = fields.IntField(null=True)

    class Meta:
        ordering = ["order"]
        table = "rvc_rvcmodel"


RVCModelSchema = pydantic_model_creator(RVCModel, name="RVCModelSchema")
