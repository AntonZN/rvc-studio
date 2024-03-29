# Generated by Django 5.0.1 on 2024-01-30 08:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("studio", "0003_tts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="status",
            field=models.CharField(
                choices=[
                    ("done", "Done"),
                    ("error", "Error"),
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("deleted", "Deleted"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="tts",
            name="status",
            field=models.CharField(
                choices=[
                    ("done", "Done"),
                    ("error", "Error"),
                    ("pending", "Pending"),
                    ("processing", "Processing"),
                    ("deleted", "Deleted"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
    ]
