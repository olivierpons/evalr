# Generated by Django 2.2.5 on 2019-09-29 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0004_auto_20190811_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wzuserstep',
            name='step',
            field=models.CharField(blank=True, choices=[('nex-000 STEP_1', 'nex-000 - Step 1'), ('nex-010 STEP_2', 'nex-010 - Step 2'), ('nex-020 STEP_3', 'nex-020 - Step 3'), ('nlg-000 STEP_1', 'nlg-000 - Name / how many?'), ('nlg-010 STEP_2', 'nlg-010 - Step 2'), ('nlg-020 STEP_3', 'nlg-020 - Step 3'), ('nlg-020 STEP_4', 'nlg-020 - Step 4'), ('spl-000 STEP_1', 'spl-000 - Step 1'), ('spl-010 STEP_2', 'spl-010 - Step 2'), ('spl-020 STEP_3', 'spl-020 - Step 3')], default=None, max_length=200, null=True),
        ),
    ]
