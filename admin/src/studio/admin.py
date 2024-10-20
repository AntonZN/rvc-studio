import datetime

from django.contrib import admin
from .models import *

admin.site.register(Record)


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    def average_waiting_old_split(self, obj):
        date = obj.date
        start_of_day = datetime.datetime.combine(date, datetime.time.min)
        end_of_day = datetime.datetime.combine(date, datetime.time.max)
        times = ProcessRequest.objects.filter(
            process_type="old_split",
            created_at__gte=start_of_day,
            created_at__lte=end_of_day,
        ).values_list("waiting_time_in_seconds", flat=True)

        time_waiting = list(times)

        if time_waiting:
            average_time_waiting = sum(time_waiting) / len(time_waiting)
            minutes = average_time_waiting // 60
            remaining_seconds = average_time_waiting % 60
            average_time_waiting = f"{int(minutes)} min {int(remaining_seconds)} sec"
        else:
            average_time_waiting = "0"

        return average_time_waiting

    average_waiting_old_split.short_description = "average_waiting_old_split"

    list_display = (
        "date",
        "count_cover",
        "count_tts",
        "count_split",
        "count_split_old",
        "count_clone",
        "count_denoise",
        "average_waiting",
        "average_waiting_old_split",
    )
