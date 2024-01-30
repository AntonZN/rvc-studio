from django.db import models


class RVCModel(models.Model):
    ru = models.CharField("Название RU", null=True, blank=True, max_length=256)
    en = models.CharField("Название EN", null=True, blank=True, max_length=256)
    es = models.CharField("Название ES", null=True, blank=True, max_length=256)
    pt = models.CharField("Название PT", null=True, blank=True, max_length=256)
    fr = models.CharField("Название FR", null=True, blank=True, max_length=256)
    hi = models.CharField("Название HI", null=True, blank=True, max_length=256)
    ko = models.CharField("Название KO", null=True, blank=True, max_length=256)
    description = models.TextField("Описание", null=True, blank=True)
    lock = models.BooleanField(default=False)
    hide = models.BooleanField(default=False)
    image = models.FileField("Изображение", upload_to="icons", null=True, blank=True)
    file = models.FileField("Файл модели", upload_to="models/RVC")

    class Meta:
        verbose_name = "RVC модель"
        verbose_name_plural = "RVC модели"

    def __str__(self):
        if self.ru:
            return self.ru
        else:
            return str(self.id)
