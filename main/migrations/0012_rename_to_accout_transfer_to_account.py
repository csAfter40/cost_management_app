# Generated by Django 4.0.3 on 2022-04-21 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_transfer_to_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transfer',
            old_name='to_accout',
            new_name='to_account',
        ),
    ]
