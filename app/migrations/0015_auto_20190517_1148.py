# Generated by Django 2.2.1 on 2019-05-17 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20190517_1055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fusion',
            old_name='duree_crossfade',
            new_name='crossfade_length',
        ),
    ]
