# Generated by Django 2.2.1 on 2019-05-15 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20190515_1613'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='InterrogationPeople',
            new_name='InterrogationPerson',
        ),
    ]