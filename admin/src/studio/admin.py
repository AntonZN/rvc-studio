from django.contrib import admin
from .models import *

admin.site.register(Record)


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "count_cover",
        "count_tts",
        "count_split",
        "count_split_old",
        "count_clone",
    )
