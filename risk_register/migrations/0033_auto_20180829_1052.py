# Generated by Django 2.0.6 on 2018-08-29 09:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0032_auto_20180827_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='processus',
            name='risques',
            field=models.ManyToManyField(through='risk_register.ProcessusRisque', to='risk_register.Risque'),
        ),
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('S', 'Sévérité'), ('O', 'Occurence'), ('D', 'Détectabilité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 28, 9, 52, 17, 277953, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
    ]
