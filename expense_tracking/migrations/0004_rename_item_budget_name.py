# Generated by Django 4.2 on 2024-08-18 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expense_tracking', '0003_alter_budget_budget_amt_alter_budget_current_bal_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='item',
            new_name='name',
        ),
    ]
