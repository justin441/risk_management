# Generated by Django 2.0.6 on 2018-10-12 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0049_auto_20181012_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('S', 'Sévérité'), ('O', 'Occurence'), ('D', 'Détectabilité')], default='O', max_length=1, verbose_name='critère cible'),
        ),
    ]