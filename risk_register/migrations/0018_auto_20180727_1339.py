# Generated by Django 2.0.6 on 2018-07-27 12:39

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.utils.timezone import utc
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('risk_register', '0017_auto_20180727_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estimation',
            name='proprietaire',
        ),
        migrations.RemoveField(
            model_name='estimation',
            name='proprietaire_change',
        ),
        migrations.AddField(
            model_name='activiterisque',
            name='proprietaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activiterisques_manages', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire du risque'),
        ),
        migrations.AddField(
            model_name='activiterisque',
            name='proprietaire_change',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='proprietaire'),
        ),
        migrations.AddField(
            model_name='processusrisque',
            name='proprietaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processusrisques_manages', to=settings.AUTH_USER_MODEL, verbose_name='propriétaire du risque'),
        ),
        migrations.AddField(
            model_name='processusrisque',
            name='proprietaire_change',
            field=model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='proprietaire'),
        ),
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('S', 'Sévérité'), ('O', 'Occurence'), ('D', 'Détectabilité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 9, 25, 12, 39, 44, 438570, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
    ]
