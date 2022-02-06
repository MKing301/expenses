from django.shortcuts import render
from .models import Expense


def expenses(request):
    my_expenses = Expense.objects.order_by('-expense_date')
    return render(request=request,
                  template_name="expense_tracking/expense.html",
                  context={
                      'my_expenses': my_expenses
                  }
                  )
