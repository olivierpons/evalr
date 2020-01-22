# Generated by Django 2.2.4 on 2019-08-08 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0002_auto_20190802_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wzuserstep',
            name='step',
            field=models.CharField(blank=True, choices=[('nex-000 STEP_1', 'nex-000 - Step 1'), ('nex-010 STEP_2', 'nex-010 - Step 2'), ('nex-020 STEP_3', 'nex-020 - Step 3'), ('nlg-000 STEP_1', 'nlg-000 - Step 1'), ('nlg-010 STEP_2', 'nlg-010 - Step 2'), ('nlg-020 STEP_3', 'nlg-020 - Step 3'), ('spl-000 STEP_1', 'spl-000 - Step 1'), ('spl-010 STEP_2', 'spl-010 - Step 2'), ('spl-020 STEP_3', 'spl-020 - Step 3')], default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='wzuserstep',
            name='uuid_reference',
            field=models.CharField(choices=[(0, 'wz-example'), (1, 'wz-new-learners-group'), (2, 'wz-new-exam')], default=['wz-example', 'wz-new-learners-group', 'wz-new-exam'], max_length=200),
        ),
    ]
