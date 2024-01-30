from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class RVCModel(Model):
    id = fields.IntField(pk=True)
    ru = fields.CharField(max_length=256)
    en = fields.CharField(max_length=256)
    es = fields.CharField(max_length=256)
    pt = fields.CharField(max_length=256)
    fr = fields.CharField(max_length=256)
    hi = fields.CharField(max_length=256)
    ko = fields.CharField(max_length=256)


    class Meta:
        table = "rvc_rvcmodel"


RVCModelSchema = pydantic_model_creator(RVCModel, name="RVCModelSchema")
