# Generated by Django 2.2.3 on 2019-08-02 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_auto_20190802_1240'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Categorie',
            new_name='Category',
        ),
        migrations.AlterModelOptions(
            name='categoriesgroup',
            options={'ordering': ['description'], 'verbose_name': 'Group of categories', 'verbose_name_plural': 'Groups of categories'},
        ),
        migrations.AlterModelOptions(
            name='modeleinterrogation',
            options={'verbose_name': 'Exam template', 'verbose_name_plural': 'Exam templates'},
        ),
        migrations.AlterModelOptions(
            name='modeleinterrogationgroupexpressions',
            options={'verbose_name': 'Exam template - group of expressions', 'verbose_name_plural': 'Exam template - groups of expressions'},
        ),
        migrations.AlterModelOptions(
            name='modeleinterrogationphrase',
            options={'ordering': ['importance'], 'verbose_name': 'Exam template -sentence', 'verbose_name_plural': 'Exam template - sentences'},
        ),
        migrations.AlterModelOptions(
            name='modelesession',
            options={'ordering': ['description', 'pk'], 'verbose_name': 'Exam template - Session', 'verbose_name_plural': 'Exam template - Sessions'},
        ),
        migrations.AlterField(
            model_name='groupecategoriesregles',
            name='categoriesgroup_1',
            field=models.ForeignKey(help_text='Groups of categories of the current expression', on_delete=django.db.models.deletion.CASCADE, related_name='gc1', to='app.CategoriesGroup'),
        ),
        migrations.AlterField(
            model_name='groupecategoriesregles',
            name='categoriesgroup_2',
            field=models.ForeignKey(help_text='Groups of categories of the next expression', on_delete=django.db.models.deletion.CASCADE, related_name='gc2', to='app.CategoriesGroup'),
        ),
    ]
