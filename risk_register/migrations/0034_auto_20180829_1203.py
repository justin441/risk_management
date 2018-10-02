# Generated by Django 2.0.6 on 2018-08-29 11:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0033_auto_20180829_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('O', 'Occurence'), ('D', 'Détectabilité'), ('S', 'Sévérité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de revue'),
        ),
    ]