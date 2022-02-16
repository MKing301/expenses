from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, ExpenseType
from .forms import ExpenseForm, AuthenticationFormWithCaptchaField
from django.contrib.auth import (
    login, logout, authenticate)
from django.contrib import messages
from .signals import log_user_logout
from django.contrib.auth.decorators import login_required


def index(request):
    return render(
        request=request,
        template_name="expense_tracking/index.html",
    )


def login_request(request):

    # Verify the user is not logged into the application
    if not request.user.is_authenticated:

        # For user submitting the form
        if request.method == "POST":
            form = AuthenticationFormWithCaptchaField(
                request, data=request.POST
            )

            # If the form is valid, present user with a success alert
            # and redirect the the expense list
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

            # Check if the users exist
            elif User.objects.filter(
                    username=form.cleaned_data.get('username')).exists():
                user = User.objects.filter(
                    username=form.cleaned_data.get('username')).values()

                # If the user's profile is inactive, alert the user to
                # contact the admin
                if(user[0]['is_active'] is False):
                    messages.info(
                        request,
                        "Contact the administrator to activate your account!"
                    )
                    return redirect("expense_tracking:login_request")

                # Present form to the user with any errors
                else:
                    return render(
                        request=request,
                        template_name="expense_tracking/login.html",
                        context={"form": form}
                    )

            # Present form to the user with any errors
            else:
                return render(
                    request=request,
                    template_name="expense_tracking/login.html",
                    context={"form": form}
                )

        # When the form is NOT being submitted, present to form to the user
        else:
            form = AuthenticationFormWithCaptchaField()
            return render(
                request=request,
                template_name="expense_tracking/login.html",
                context={"form": form}
            )

    # If the user is already logged into the application, provide alert
    # to inform the user and redirect her/him to the expenses list
    else:
        messages.info(
            request,
            '''You are already logged in.  You must log out to log in as
            another user.'''
        )
        return redirect("expense_tracking:expenses")


@login_required()
def expenses(request):
    my_expenses = Expense.objects.order_by('-expense_date')
    return render(request=request,
                  template_name="expense_tracking/expense.html",
                  context={
                      'my_expenses': my_expenses
                  }
                  )


@login_required()
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


@login_required
def edit_expense(request, id):

    # Obtain expense record to edit by id
    expense_to_edit = Expense.objects.get(id=id)

    # Obtain list of expense types in order by name, except the selected value
    # by id from the form
    expense_types = ExpenseType.objects.exclude(
        id=expense_to_edit.expense_type.pk
    ).order_by('name')

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense_to_edit)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your expense was updated successfully!'
            )
        return redirect('expense_tracking:expenses')

    else:
        form = ExpenseForm(instance=expense_to_edit)
        return render(
            request=request,
            template_name='expense_tracking/edit_expense.html',
            context={
                'expense_types': expense_types,
                'expense_to_edit': expense_to_edit,
                'form': form
            }
        )


@login_required()
def delete_expense(request, id):
    expense_to_delete = Expense.objects.get(id=id)
    expense_to_delete.delete()
    messages.success(
        request,
        f'''Expense named {expense_to_delete.name} dated
        {expense_to_delete.expense_date} was successfully deleted!'''
    )
    return redirect('expense_tracking:expenses')


@login_required()
def logout_request(request):
    logout(request)
    log_user_logout()
    return redirect("catalog:index")
