from django.shortcuts import render


def expenses(request):
    return render(request=request,
                  template_name="expense_tracking/expense.html"
                  )
