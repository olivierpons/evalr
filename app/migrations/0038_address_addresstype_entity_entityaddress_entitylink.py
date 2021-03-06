# Generated by Django 2.2.4 on 2019-08-11 07:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_auto_20190802_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Last changed')),
                ('date_v_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='V. start')),
                ('date_v_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='V. end')),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ['date_v_start'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AddressType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Last changed')),
                ('date_v_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='V. start')),
                ('date_v_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='V. end')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ['date_v_start'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Last changed')),
                ('date_v_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='V. start')),
                ('date_v_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='V. end')),
                ('is_physical', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['date_v_start'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EntityLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Last changed')),
                ('date_v_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='V. start')),
                ('date_v_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='V. end')),
                ('link_type', models.IntegerField(choices=[(1, 'Parent <> Child'), (2, 'Husband <> Wife'), (3, 'Teacher <> Student')], default=3)),
                ('dst', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dst', to='app.Entity')),
                ('src', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='src', to='app.Entity')),
            ],
            options={
                'verbose_name': 'Relation',
                'verbose_name_plural': 'Relations',
            },
        ),
        migrations.CreateModel(
            name='EntityAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Last changed')),
                ('date_v_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='V. start')),
                ('date_v_end', models.DateTimeField(blank=True, default=None, null=True, verbose_name='V. end')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Address')),
                ('address_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.AddressType')),
                ('entity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Entity')),
            ],
            options={
                'ordering': ['date_v_start'],
                'abstract': False,
            },
        ),
    ]
