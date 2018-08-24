# Generated by Django 2.0.6 on 2018-08-24 09:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('risk_register', '0023_auto_20180824_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='risque',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='risque',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='estimation',
            name='date_revue',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 23, 9, 43, 20, 568367, tzinfo=utc), verbose_name='revue prevue pour le'),
        ),
    ]
