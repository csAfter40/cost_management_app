# Generated by Django 4.0.3 on 2022-07-10 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_category_is_protected'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_loan',
            field=models.BooleanField(default=False),
        ),
    ]
