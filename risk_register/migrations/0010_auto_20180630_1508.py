# Generated by Django 2.0.6 on 2018-06-30 14:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0009_auto_20180630_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('S', 'Sévérité'), ('O', 'Occurence'), ('D', 'Détectabilité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 29, 14, 8, 56, 996031, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
    ]