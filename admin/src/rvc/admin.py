from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from .models import RVCModel, Project, RVCModelInfo


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(RVCModel)
class RVCModelAdmin(OrderedModelAdmin):
    list_display = ("__str__", "move_up_down_links")


@admin.register(RVCModelInfo)
class RVCModelInfoAdmin(OrderedModelAdmin):
    list_display = (
        "__str__",
        "project",
        "move_up_down_links",
    )
    list_filter = ("project",)
