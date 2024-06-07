from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from .models import RVCModel, Project, RVCModelInfo, Category


@admin.register(Category)
class CategoryAdmin(OrderedModelAdmin):
    list_display = ("__str__", "move_up_down_links")
    search_fields = ["name"]
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    pass


@admin.register(RVCModel)
class RVCModelAdmin(OrderedModelAdmin):
    list_display = ("__str__", "move_up_down_links")


@admin.register(RVCModelInfo)
class RVCModelInfoAdmin(OrderedModelAdmin):
    autocomplete_fields = ["project", "categories"]

    list_display = (
        "__str__",
        "project",
        "move_up_down_links",
    )
    list_filter = ("project",)
