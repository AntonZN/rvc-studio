from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class Project(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, null=True)

    class Meta:
        table = "rvc_project"


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, null=True)
    order = fields.IntField(null=True)

    class Meta:
        table = "rvc_category"


class RVCModel(Model):
    id = fields.IntField(pk=True)
    ru = fields.CharField(max_length=256, null=True)
    order = fields.IntField(null=True)
    speaker = fields.CharField(max_length=256, null=True)
    lang = fields.CharField(max_length=256, null=True)
    gender = fields.CharField(max_length=256, null=True)

    class Meta:
        ordering = ["order"]
        table = "rvc_rvcmodel"


class RVCModelInfo(Model):
    id = fields.IntField(pk=True)
    model = fields.ForeignKeyField("models.RVCModel", related_name="model_info")
    project = fields.ForeignKeyField("models.Project", related_name="models")
    categories = fields.ManyToManyField(
        "models.Category",
        related_name="models",
        through="rvc_rvcmodelinfo_categories",
        forward_key="category_id",
        backward_key="rvcmodelinfo_id",
    )
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
    audio_example = fields.TextField(null=True)
    order = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    usages = fields.IntField(default=0)

    class Meta:
        ordering = ["order"]
        table = "rvc_rvcmodelinfo"


class RVCModelInfoCategory(Model):
    rvcmodelinfo = fields.ForeignKeyField(
        "models.RVCModelInfo", related_name="category_links"
    )
    category = fields.ForeignKeyField("models.Category", related_name="modelinfo_links")

    class Meta:
        table = "rvc_rvcmodelinfo_categories"


RVCModelSchema = pydantic_model_creator(RVCModel, name="RVCModelSchema")
CategorySchema = pydantic_model_creator(Category, name="CategorySchema")
