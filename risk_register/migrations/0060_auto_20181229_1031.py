# Generated by Django 2.0.6 on 2018-12-29 09:31

from django.db import migrations, models
import model_utils.fields
import risk_register.models


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0059_auto_20181124_0911'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='processus',
            options={'ordering': ('nom',), 'verbose_name': 'processus', 'verbose_name_plural': 'processus'},
        ),
        migrations.AlterField(
            model_name='activiterisque',
            name='date_revue',
            field=models.DateTimeField(blank=True, default=risk_register.models.risk_default_review_date, null=True, verbose_name='revue'),
        ),
        migrations.AlterField(
            model_name='activiterisque',
            name='verifie_le',
            field=model_utils.fields.MonitorField(default=None, monitor='verifie', when={'verified'}),
        ),
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('D', 'Détectabilité'), ('S', 'Sévérité'), ('O', 'Occurence')], default='O', max_length=1, verbose_name='critère cible'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=risk_register.models.estimation_default_review_date, verbose_name='Date de revue'),
        ),
        migrations.AlterField(
            model_name='processusrisque',
            name='date_revue',
            field=models.DateTimeField(blank=True, default=risk_register.models.risk_default_review_date, null=True, verbose_name='revue'),
        ),
        migrations.AlterField(
            model_name='processusrisque',
            name='verifie_le',
            field=model_utils.fields.MonitorField(default=None, monitor='verifie', when={'verified'}),
        ),
    ]
