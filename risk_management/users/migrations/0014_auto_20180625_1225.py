# Generated by Django 2.0.6 on 2018-06-25 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20180613_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='fonction',
            field=models.CharField(help_text='entrez "general manager" si directeur général d\'entité,                                 ou "project manager" s\'il s\'agit d\'un chef de projet', max_length=100, verbose_name='poste'),
        ),
    ]
