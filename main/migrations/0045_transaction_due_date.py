# Generated by Django 4.0.3 on 2023-02-20 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_transaction_installments_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]