from django.db import models


class ExpenseType(models.Model):
    # Class for expense type

    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        # String method returns expense type name

        return self.name


class Expense(models.Model):
    # Class for expense

    expense_date = models.DateField()
    expense_type = models.ForeignKey(
        ExpenseType,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    org = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    notes = models.CharField(max_length=200, blank=True)

    def __str__(self):
        # String method returns expense name and date

        return self.name + '_' + self.expense_date.strftime('%m_%d_%Y')
