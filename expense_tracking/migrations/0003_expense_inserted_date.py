# Generated by Django 4.0.2 on 2022-03-13 18:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('expense_tracking', '0002_alter_expense_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='inserted_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
