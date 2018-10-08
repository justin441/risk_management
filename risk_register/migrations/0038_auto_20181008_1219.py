# Generated by Django 2.0.6 on 2018-10-08 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0037_auto_20181008_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('D', 'Détectabilité'), ('O', 'Occurence'), ('S', 'Sévérité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
    ]
