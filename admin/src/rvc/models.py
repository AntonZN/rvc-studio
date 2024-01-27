from django.db import models


class RVCModel(models.Model):
    name = models.CharField("Название модели", max_length=256)
    file = models.FileField("Файл модели", upload_to="models/RVC")

    class Meta:
        verbose_name = "RVC модель"
        verbose_name_plural = "RVC модели"

    def __str__(self):
        return self.name
