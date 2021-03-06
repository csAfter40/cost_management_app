# Generated by Django 4.0.3 on 2022-06-25 17:27

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_expensecategory_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('type', models.CharField(choices=[('E', 'Expense'), ('I', 'Income')], max_length=1)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='main.category')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'unique_together': {('parent', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('date', models.DateField(blank=True, default=datetime.date.today)),
                ('type', models.CharField(choices=[('E', 'Expense'), ('I', 'Income'), ('T', 'Transfer')], max_length=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.account')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.category')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='expensecategory',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='expensecategory',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='expensecategory',
            name='user',
        ),
        migrations.RemoveField(
            model_name='income',
            name='account',
        ),
        migrations.RemoveField(
            model_name='income',
            name='category',
        ),
        migrations.AlterUniqueTogether(
            name='incomecategory',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='incomecategory',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='incomecategory',
            name='user',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='from_account',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='from_amount',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='to_account',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='to_amount',
        ),
        migrations.AddField(
            model_name='transfer',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transfer',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='Expense',
        ),
        migrations.DeleteModel(
            name='ExpenseCategory',
        ),
        migrations.DeleteModel(
            name='Income',
        ),
        migrations.DeleteModel(
            name='IncomeCategory',
        ),
        migrations.AddField(
            model_name='transfer',
            name='from_transaction',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transfers_from', to='main.transaction'),
        ),
        migrations.AddField(
            model_name='transfer',
            name='to_transaction',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transfers_to', to='main.transaction'),
        ),
    ]
