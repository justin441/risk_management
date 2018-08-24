# Generated by Django 2.0.6 on 2018-08-24 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20180823_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessunit',
            name='bu_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bu_manages', to=settings.AUTH_USER_MODEL, verbose_name='manager'),
        ),
    ]
