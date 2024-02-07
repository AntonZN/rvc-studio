from django.db import models

from ordered_model.models import OrderedModel

class Lang(models.TextChoices):
    RU: str = "ru"
    DE: str = "de"
    EN: str = "en"
    ES: str = "es"
    FR: str = "fr"
    HI: str = "hi"
    IT: str = "it"
    JA: str = "ja"
    KO: str = "ko"
    PL: str = "pl"
    PT: str = "pt"
    TR: str = "tr"
    ZH: str = "zh"


class Speaker(models.TextChoices):
    NULL: str = "0"
    ONE: str = "1"
    TWO: str = "2"
    FRE: str = "3"
    FOUR: str = "4"
    FIVE: str = "5"
    SIX: str = "6"
    SEVEN: str = "7"
    EIGHT: str = "8"
    NINE: str = "9"


class RVCModel(OrderedModel):
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
    speaker = models.CharField("Спикер", choices=Speaker.choices, null=True, blank=True)
    lang = models.CharField("Язык", choices=Lang.choices, null=True, blank=True)

    class Meta:
        verbose_name = "RVC модель"
        verbose_name_plural = "RVC модели"
        ordering = ("order",)

    def __str__(self):
        if self.ru:
            return self.ru
        else:
            return str(self.id)
