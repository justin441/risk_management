# Generated by Django 2.0.6 on 2019-01-22 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0062_auto_20190122_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('D', 'Détectabilité'), ('S', 'Sévérité'), ('O', 'Occurence')], default='O', max_length=1, verbose_name='critère cible'),
        ),
    ]
