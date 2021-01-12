# Generated by Django 3.0.3 on 2020-03-24 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200324_2017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitytype',
            name='text',
        ),
        migrations.AddField(
            model_name='activitytype',
            name='type',
            field=models.IntegerField(choices=[(1, 'Unknown'), (2, 'Profession')], default=1),
        ),
    ]
