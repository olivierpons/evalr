# Generated by Django 2.2.3 on 2019-08-02 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_auto_20190802_1231'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoriesgroupcategory',
            old_name='categorie',
            new_name='category',
        ),
    ]
