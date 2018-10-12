# Generated by Django 2.0.6 on 2018-10-04 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0035_auto_20180829_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controle',
            name='critere_cible',
            field=models.CharField(choices=[('D', 'Détectabilité'), ('S', 'Sévérité'), ('O', 'Occurence')], default='O', max_length=1, verbose_name='critère cible'),
        ),
    ]