# Generated by Django 2.2.3 on 2019-08-02 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_auto_20190802_1245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modeleinterrogationphrase',
            options={'ordering': ['importance'], 'verbose_name': 'Exam template - sentence', 'verbose_name_plural': 'Exam template - sentences'},
        ),
    ]
