# Generated by Django 2.0.6 on 2018-06-13 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20180612_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessunit',
            name='projet',
            field=models.BooleanField(default=False, help_text='Le Business Unit est-il un Projet?'),
        ),
    ]
