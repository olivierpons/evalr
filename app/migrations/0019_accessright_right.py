# Generated by Django 2.2.1 on 2019-06-06 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_accessright'),
    ]

    operations = [
        migrations.AddField(
            model_name='accessright',
            name='right',
            field=models.IntegerField(choices=[(1, 'Read (R)'), (2, 'Write (W)'), (3, 'Read/Write (RW)')], default=1),
        ),
    ]
