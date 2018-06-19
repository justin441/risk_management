# Generated by Django 2.0.6 on 2018-06-15 12:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0003_auto_20180615_1216'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='controle',
            options={'get_latest_by': 'created', 'ordering': ('start',), 'verbose_name': 'Contrôle', 'verbose_name_plural': 'Contrôles'},
        ),
        migrations.AlterModelOptions(
            name='estimation',
            options={'get_latest_by': 'created', 'ordering': ('-created',), 'verbose_name': 'Estimation du risque', 'verbose_name_plural': 'Estimations des risque'},
        ),
        migrations.AlterField(
            model_name='activite',
            name='description',
            field=models.CharField(blank=True, max_length=500, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='activiterisque',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 15, 12, 10, 46, 44270, tzinfo=utc), verbose_name='revue prévue pour le: '),
        ),
        migrations.AlterField(
            model_name='activiterisque',
            name='verifie_le',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='verifie'),
        ),
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('D', 'Détectabilité'), ('O', 'Occurence'), ('S', 'Sévérité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='controle',
            name='nom',
            field=models.CharField(max_length=300, verbose_name='nom'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 14, 12, 10, 46, 49270, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
        migrations.AlterField(
            model_name='processusrisque',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 15, 12, 10, 46, 44270, tzinfo=utc), verbose_name='revue prévue pour le: '),
        ),
        migrations.AlterField(
            model_name='processusrisque',
            name='verifie_le',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='verifie'),
        ),
    ]
