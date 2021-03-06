# Generated by Django 4.0.3 on 2022-04-13 04:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_cost_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='cost',
            name='date',
            field=models.DateField(blank=True, default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='cost',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='income',
            name='date',
            field=models.DateField(blank=True, default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='income',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
