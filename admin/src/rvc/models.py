from django.db import models


class RVCModel(models.Model):
    ru = models.CharField("Название RU", max_length=256)
    en = models.CharField("Название EN", max_length=256)
    es = models.CharField("Название ES", max_length=256)
    pt = models.CharField("Название PT", max_length=256)
    fr = models.CharField("Название FR", max_length=256)
    hi = models.CharField("Название HI", max_length=256)
    ko = models.CharField("Название KO", max_length=256)
    file = models.FileField("Файл модели", upload_to="models/RVC")

    class Meta:
        verbose_name = "RVC модель"
        verbose_name_plural = "RVC модели"

    def __str__(self):
        return self.name
