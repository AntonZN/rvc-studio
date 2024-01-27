from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class RVCModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256)

    class Meta:
        table = "rvc_rvcmodel"


RVCModelSchema = pydantic_model_creator(RVCModel, name="RVCModelSchema")
