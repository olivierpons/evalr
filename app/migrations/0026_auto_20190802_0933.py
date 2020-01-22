# Generated by Django 2.2.3 on 2019-08-02 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20190802_0151'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expressionvoice',
            options={'verbose_name': 'Expression voice', 'verbose_name_plural': 'Expression voices'},
        ),
        migrations.AlterModelOptions(
            name='groupemots',
            options={'ordering': ['description'], 'verbose_name': 'Expressions group', 'verbose_name_plural': 'Expressions groups'},
        ),
        migrations.RenameField(
            model_name='groupemots',
            old_name='mots',
            new_name='expressions',
        ),
    ]
