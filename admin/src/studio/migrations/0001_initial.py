# Generated by Django 5.0.1 on 2024-01-20 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClonedRecord',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('file_path', models.TextField()),
                ('status', models.CharField(choices=[('done', 'Done'), ('error', 'Error'), ('pending', 'Pending'), ('deleted', 'Deleted')], default='pending', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('path', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoverRecord',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('file_path', models.TextField()),
                ('status', models.CharField(choices=[('done', 'Done'), ('error', 'Error'), ('pending', 'Pending'), ('deleted', 'Deleted')], default='pending', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('path', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SplitRecord',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('file_path', models.TextField()),
                ('status', models.CharField(choices=[('done', 'Done'), ('error', 'Error'), ('pending', 'Pending'), ('deleted', 'Deleted')], default='pending', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('vocal_path', models.TextField(blank=True, null=True)),
                ('instrumental_path', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
