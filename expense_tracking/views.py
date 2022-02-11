from django.shortcuts import render, redirect
from .models import Expense, ExpenseType
from .forms import ExpenseForm
from django.contrib import messages


def expenses(request):
    my_expenses = Expense.objects.order_by('-expense_date')
    return render(request=request,
                  template_name="expense_tracking/expense.html",
                  context={
                      'my_expenses': my_expenses
                  }
                  )


def add_expense(request):

    expense_types = ExpenseType.objects.order_by('name')

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Expense added successfully.'
            )
            return redirect('expense_tracking:expenses')

        else:
            return render(
                request=request,
                template_name="expense_tracking/add_expense.html",
                context={
                    'form': form,
                    'expense_types': expense_types
                }
            )
    else:
        form = ExpenseForm()

        return render(
            request=request,
            template_name="expense_tracking/add_expense.html",
            context={
                'form': form,
                'expense_types': expense_types
            }
        )


def delete_expense(request, id):
    expense_to_delete = Expense.objects.get(id=id)
    expense_to_delete.delete()
    messages.success(
        request,
        f'''Expense named {expense_to_delete.name} dated
        {expense_to_delete.expense_date} was successfully deleted!'''
    )
    return redirect('expense_tracking:expenses')
