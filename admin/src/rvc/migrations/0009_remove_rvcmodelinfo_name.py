# Generated by Django 4.1.7 on 2024-02-14 05:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rvc", "0008_project_remove_rvcmodel_description_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rvcmodelinfo",
            name="name",
        ),
    ]