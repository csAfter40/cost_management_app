# Generated by Django 4.0.3 on 2022-08-31 05:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_transaction_content_type_transaction_object_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='account',
        ),
    ]
