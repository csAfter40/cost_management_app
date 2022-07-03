# Generated by Django 4.0.3 on 2022-06-27 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_transfer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('E', 'Expense'), ('I', 'Income'), ('TI', 'Transfer In'), ('TO', 'Transfer Out')], max_length=2),
        ),
    ]