# Generated by Django 2.2.3 on 2019-08-02 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20190802_1225'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GroupeCategoriesCategorie',
            new_name='CategoriesGroupCategory',
        ),
    ]
