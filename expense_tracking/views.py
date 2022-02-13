from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, ExpenseType
from .forms import ExpenseForm, AuthenticationFormWithCaptchaField
from django.contrib.auth import (
    login, authenticate)
from django.contrib import messages


def login_request(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = AuthenticationFormWithCaptchaField(
                request, data=request.POST
            )
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                login(request, user)
                messages.success(
                    request,
                    f'{username} logged in successfully.'
                )
                return redirect("expense_tracking:expenses")

            elif User.objects.filter(
                    username=form.cleaned_data.get('username')).exists():
                user = User.objects.filter(
                    username=form.cleaned_data.get('username')).values()
                if(user[0]['is_active'] is False):
                    messages.info(
                        request,
                        "Contact the administrator to activate your account!"
                    )
                    return redirect("expense_tracking:expenses")

                else:
                    return render(
                        request=request,
                        template_name="expense_tracking/login.html",
                        context={"form": form}
                    )

            else:
                return render(
                    request=request,
                    template_name="expense_tracking/login.html",
                    context={"form": form}
                )
        else:
            form = AuthenticationFormWithCaptchaField()
            return render(
                request=request,
                template_name="expense_tracking/login.html",
                context={"form": form}
            )
    else:
        messages.info(
            request,
            '''You are already logged in.  You must log out to log in as
            another user.'''
        )
        return redirect("expense_tracking:expenses")


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
