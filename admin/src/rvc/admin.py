from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from .models import RVCModel


@admin.register(RVCModel)
class RVCModelAdmin(OrderedModelAdmin):
    list_display = ("__str__", "order", "move_up_down_links")
    list_editable = ("order",)