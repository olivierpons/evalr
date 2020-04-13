# Generated by Django 2.2.1 on 2019-06-07 15:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_accessright_right'),
    ]

    operations = [
        migrations.CreateModel(
            name='Langue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Last changed')),
                ('date_v_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='V. start')),
                ('date_v_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='V. end')),
                ('nom', models.CharField(max_length=50)),
                ('nom_local', models.CharField(default='', max_length=50)),
                ('locale', models.CharField(max_length=2)),
                ('bidirectionnel', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Languages',
                'ordering': ['date_v_start'],
                'abstract': False,
            },
        ),
    ]