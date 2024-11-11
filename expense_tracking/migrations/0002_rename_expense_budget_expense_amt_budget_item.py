# Generated by Django 4.2 on 2024-08-18 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense_tracking', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='expense',
            new_name='expense_amt',
        ),
        migrations.AddField(
            model_name='budget',
            name='item',
            field=models.CharField(default='Food', max_length=200),
        ),
    ]
