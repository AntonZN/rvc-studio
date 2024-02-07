from django.db import models

from ordered_model.models import OrderedModel

class Lang(models.TextChoices):
    RU: str = ("ru", "ru")
    DE: str = ("de", "de")
    EN: str = ("en", "en")
    ES: str = ("es", "es")
    FR: str = ("fr", "fr")
    HI: str = ("hi", "hi")
    IT: str = ("it", "it")
    JA: str = ("ja", "ja")
    KO: str = ("ko", "ko")
    PL: str = ("pl", "pl")
    PT: str = ("pt", "pt")
    TR: str = ("tr", "tr")
    ZH: str = ("zh", "zh")


class Speaker(models.TextChoices):
    NULL: str = ("0", "0")
    ONE: str = ("1", "1")
    TWO: str = ("2", "2")
    FRE: str = ("3", "3")
    FOUR: str = ("4", "4")
    FIVE: str = ("5", "5")
    SIX: str = ("6", "6")
    SEVEN: str = ("7", "7")
    EIGHT: str = ("8", "8")
    NINE: str = ("9", "9")


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
    speaker = models.CharField("Спикер", choices=Speaker.choices, null=True, blank=True, max_length=128)
    lang = models.CharField("Язык", choices=Lang.choices, null=True, blank=True, max_length=128)

    class Meta:
        verbose_name = "RVC модель"
        verbose_name_plural = "RVC модели"
        ordering = ("order",)

    def __str__(self):
        if self.ru:
            return self.ru
        else:
            return str(self.id)
