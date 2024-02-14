from django.db import models

from ordered_model.models import OrderedModel


class Lang(models.TextChoices):
    RU = "ru", "ru"
    DE = "de", "de"
    EN = "en", "en"
    ES = "es", "es"
    FR = "fr", "fr"
    HI = "hi", "hi"
    IT = "it", "it"
    JA = "ja", "ja"
    KO = "ko", "ko"
    PL = "pl", "pl"
    PT = "pt", "pt"
    TR = "tr", "tr"
    ZH = "zh", "zh"


class Speaker(models.TextChoices):
    NULL = "0", "0"
    ONE = "1", "1"
    TWO = "2", "2"
    FRE = "3", "3"
    FOUR = "4", "4"
    FIVE = "5", "5"
    SIX = "6", "6"
    SEVEN = "7", "7"
    EIGHT = "8", "8"
    NINE = "9", "9"


class Gender(models.TextChoices):
    WOMAN = "woman", "Женщина"
    MAN = "man", "Мужчина"


class Project(models.Model):
    name = models.CharField(
        "Название проекта",
        max_length=256,
        help_text="Вводите тут название типа app_tts или app_clone",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name


class RVCModel(OrderedModel):
    ru = models.CharField("Название", null=True, max_length=256)
    file = models.FileField("Файл модели", upload_to="models/RVC")
    speaker = models.CharField(
        "Спикер", choices=Speaker.choices, null=True, blank=True, max_length=128
    )
    lang = models.CharField(
        "Язык", choices=Lang.choices, null=True, blank=True, max_length=128
    )
    gender = models.CharField(
        "Пол", choices=Lang.choices, null=True, blank=True, max_length=128
    )

    class Meta:
        verbose_name = "RVC модель"
        verbose_name_plural = "RVC модели"
        ordering = ("order",)

    def __str__(self):
        return self.ru


class RVCModelInfo(OrderedModel):
    name = models.CharField("Названия для выбора в проекте", max_length=128)
    model = models.ForeignKey(
        RVCModel,
        on_delete=models.CASCADE,
        related_name="model_info",
        verbose_name="RVC модель",
    )
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Проект"
    )
    ru = models.CharField("Название RU", max_length=256)
    en = models.CharField("Название EN", null=True, blank=True, max_length=256)
    es = models.CharField("Название ES", null=True, blank=True, max_length=256)
    pt = models.CharField("Название PT", null=True, blank=True, max_length=256)
    fr = models.CharField("Название FR", null=True, blank=True, max_length=256)
    hi = models.CharField("Название HI", null=True, blank=True, max_length=256)
    ko = models.CharField("Название KO", null=True, blank=True, max_length=256)
    description = models.TextField("Описание", null=True, blank=True)
    image = models.FileField("Изображение", upload_to="icons", null=True, blank=True)
    lock = models.BooleanField(default=False)
    hide = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Описание модели"
        verbose_name_plural = "Описания моделей"
        ordering = ("order",)

    def __str__(self):
        return self.name
