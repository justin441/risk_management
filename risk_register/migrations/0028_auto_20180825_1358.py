# Generated by Django 2.0.6 on 2018-08-25 12:58

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0027_auto_20180825_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 24, 12, 58, 25, 93801, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
    ]