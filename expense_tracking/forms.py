from django import forms
from .models import Expense
from django.core.exceptions import ValidationError


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = (
            'expense_date',
            'expense_type',
            'name',
            'org',
            'amount',
            'notes'
        )

    def clean_expense_date(self):
        expense_date = self.cleaned_data['expense_date']
        if expense_date is None:
            raise ValidationError('Please select an expense date.')
        return expense_date

    def clean_expense_type(self):
        expense_type = self.cleaned_data['expense_type']
        if expense_type is None:
            raise ValidationError('Please enter an expense type.')
        return expense_type

    def clean_name(self):
        name = self.cleaned_data['name']
        if name is None:
            raise ValidationError('Please enter a name.')
        return name

    def clean_org(self):
        org = self.cleaned_data['org']
        if org is None:
            raise ValidationError('Please enter a org.')
        return org

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount is None:
            raise ValidationError('Please enter a amount.')
        return amount

    def save(self, commit=True):
        expense = super(ExpenseForm, self).save(commit=False)
        expense.expense_date = self.cleaned_data['expense_date']
        expense.expense_type = self.cleaned_data['expense_type']
        expense.name = self.cleaned_data['name']
        expense.org = self.cleaned_data['org']
        expense.amount = self.cleaned_data['amount']
        expense.notes = self.cleaned_data['notes']
        if commit:
            expense.save()
            return expense
