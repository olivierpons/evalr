# Generated by Django 2.2.4 on 2019-08-11 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_auto_20190811_1003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='date_creation',
        ),
        migrations.RemoveField(
            model_name='person',
            name='date_last_modif',
        ),
        migrations.RemoveField(
            model_name='person',
            name='date_v_end',
        ),
        migrations.RemoveField(
            model_name='person',
            name='date_v_start',
        ),
    ]
