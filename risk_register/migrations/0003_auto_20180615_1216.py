# Generated by Django 2.0.6 on 2018-06-15 11:16

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('risk_register', '0002_auto_20180615_0953'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activiterisque',
            options={'get_latest_by': 'created', 'verbose_name': "risque de l'activité", 'verbose_name_plural': 'risques des activités'},
        ),
        migrations.AlterModelOptions(
            name='processdata',
            options={'ordering': ['nom'], 'verbose_name': 'données du processus', 'verbose_name_plural': 'données des processus'},
        ),
        migrations.AlterModelOptions(
            name='processusrisque',
            options={'get_latest_by': 'created', 'ordering': ('created', 'processus'), 'verbose_name': 'risque du processus', 'verbose_name_plural': 'risques des processus'},
        ),
        migrations.AddField(
            model_name='activiterisque',
            name='verifie_le',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor=model_utils.fields.StatusField(choices=[(0, 'dummy')], max_length=100, no_check_for_status=True, verbose_name='vérification')),
        ),
        migrations.AddField(
            model_name='activiterisque',
            name='verifie_par',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='estimation',
            name='proprietaire_change',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='proprietaire'),
        ),
        migrations.AddField(
            model_name='processusrisque',
            name='verifie_le',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor=model_utils.fields.StatusField(choices=[(0, 'dummy')], max_length=100, no_check_for_status=True, verbose_name='vérification')),
        ),
        migrations.AddField(
            model_name='processusrisque',
            name='verifie_par',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='activiterisque',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 15, 11, 16, 13, 394062, tzinfo=utc), verbose_name='revue prévue pour le: '),
        ),
        migrations.AlterField(
            model_name='activiterisque',
            name='verifie',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default=0, max_length=100, no_check_for_status=True, verbose_name='vérification'),
        ),
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('O', 'Occurence'), ('S', 'Sévérité'), ('D', 'Détectabilité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 14, 11, 16, 13, 398062, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
        migrations.AlterField(
            model_name='processusrisque',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2019, 6, 15, 11, 16, 13, 394062, tzinfo=utc), verbose_name='revue prévue pour le: '),
        ),
        migrations.AlterField(
            model_name='processusrisque',
            name='verifie',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default=0, max_length=100, no_check_for_status=True, verbose_name='vérification'),
        ),
    ]
