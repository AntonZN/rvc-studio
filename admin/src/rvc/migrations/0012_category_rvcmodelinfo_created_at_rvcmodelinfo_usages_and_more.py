# Generated by Django 5.0.1 on 2024-06-07 01:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rvc", "0011_rvcmodelinfo_audio_example"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        db_index=True, editable=False, verbose_name="order"
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=256, verbose_name="Название Категории"),
                ),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
                "ordering": ("order",),
            },
        ),
        migrations.AddField(
            model_name="rvcmodelinfo",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата создания",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rvcmodelinfo",
            name="usages",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="rvcmodelinfo",
            name="categories",
            field=models.ManyToManyField(to="rvc.category", verbose_name="Категории"),
        ),
    ]
