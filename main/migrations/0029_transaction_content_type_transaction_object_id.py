# Generated by Django 4.0.3 on 2022-08-30 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('main', '0028_loan_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='content_type',
            field=models.ForeignKey(default=9, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='object_id',
            field=models.PositiveIntegerField(default=7),
        ),
    ]