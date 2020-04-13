# Generated by Django 2.2.3 on 2019-08-02 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wzuserstep',
            name='step',
            field=models.CharField(blank=True, choices=[('ex-000 STEP_1', 'ex-000 - Step 1'), ('ex-010 STEP_2', 'ex-010 - Step 2'), ('ex-020 STEP_3', 'ex-020 - Step 3'), ('ne-000 STEP_1', 'ne-000 - Step 1'), ('ne-010 STEP_2', 'ne-010 - Step 2'), ('ne-020 STEP_3', 'ne-020 - Step 3')], default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='wzuserstep',
            name='uuid_reference',
            field=models.CharField(choices=[(0, 'wz-example'), (1, 'wz-new-exam')], default=['wz-example', 'wz-new-exam'], max_length=200),
        ),
    ]