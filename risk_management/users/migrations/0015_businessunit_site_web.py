# Generated by Django 2.0.6 on 2018-06-29 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20180625_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessunit',
            name='site_web',
            field=models.URLField(null=True, verbose_name='site internet'),
        ),
    ]