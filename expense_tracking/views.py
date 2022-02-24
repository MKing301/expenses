from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, ExpenseType
from .forms import ExpenseForm, AuthenticationFormWithCaptchaField
from django.contrib.auth import (
    login, logout, authenticate)
from django.contrib import messages
from .signals import log_user_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework import viewsets
from .serializers import ExpenseTypeSerializer


class ExpenseTypeView(viewsets.ModelViewSet):
    # Class for expense type view set

    # Select all expense types
    queryset = ExpenseType.objects.all()

    # Serialize class
    serializer_class = ExpenseTypeSerializer


def index(request):
    # Function renders landing page

    return render(
        request=request,
        template_name="expense_tracking/index.html",
    )


def login_request(request):
    # Function for handling login request

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

        # Redirect user to table of expense
        return redirect("expense_tracking:expenses")


@login_required()
def expenses(request):
    # Function requires user to be logged in and renders a table of expenses
    # showing the date, type organization, amount and notes (with edit and
    # delete buttons)

    # Set up pagination
    # Get 20 expenses per page, by expense date descending
    p = Paginator(Expense.objects.order_by(
        '-expense_date'
    ), 20)
    page = request.GET.get('page')
    my_expenses = p.get_page(page)

    # Render expense table list 20 expense per page with page navigation at
    # the bottom of the page
    return render(request=request,
                  template_name="expense_tracking/expense.html",
                  context={
                      'my_expenses': my_expenses
                  }
                  )


@login_required()
def add_expense(request):
    # Function for adding an expense.  User must be logged in to access.

    # Obtain expense records ordered by expense name
    expense_types = ExpenseType.objects.order_by('name')

    # When the form method is post
    if request.method == "POST":

        form = ExpenseForm(request.POST)

        # Check if form is valid
        if form.is_valid():

            # If form is valid, save values to database
            form.save()

            # Display successful alert message
            messages.success(
                request,
                'Expense added successfully.'
            )

            # Redirect user to table of expense
            return redirect('expense_tracking:expenses')

        # When form is invalid
        else:

            # Render the form, including drop down values for expense types
            # and display an form field errors at the top of the page in red
            return render(
                request=request,
                template_name="expense_tracking/add_expense.html",
                context={
                    'form': form,
                    'expense_types': expense_types
                }
            )

    # When the form method is get
    else:
        # Generate expense form
        form = ExpenseForm()

        # Render the form, including drop down values for expense types
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
    # Function for adding an expense. User must be logged in to access.

    # Obtain expense record to edit by id
    expense_to_edit = Expense.objects.get(id=id)

    # Obtain list of expense types in order by name, except the selected value
    # by id from the form
    expense_types = ExpenseType.objects.exclude(
        id=expense_to_edit.expense_type.pk
    ).order_by('name')

    # When the form method is post
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense_to_edit)

        # Check if form is valid
        if form.is_valid():

            # If form is valid, save changes to database
            form.save()

            # Display successful alert message
            messages.success(
                request,
                'Your expense was updated successfully!'
            )

        # Redirect user to table of expense
        return redirect('expense_tracking:expenses')

    # When the form method is get
    else:

        # Generate expense form with selected data from edit button selected
        form = ExpenseForm(instance=expense_to_edit)

        # Render the form with populated data, including drop down values
        # for expense types
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
    # Function to delete an expense.  User must be logged in to access.

    # Obain expense to delete base on id passed from the form
    expense_to_delete = Expense.objects.get(id=id)

    # Delete the expense
    expense_to_delete.delete()

    # Display alert message stating expense date and name that was deleted.
    messages.success(
        request,
        f'''Expense named {expense_to_delete.name} dated
        {expense_to_delete.expense_date} was successfully deleted!'''
    )

    # Redirect to the table of expenses
    return redirect('expense_tracking:expenses')


@login_required()
def logout_request(request):
    # Function to log out of the application. User must be logged in to access.

    logout(request)

    # Log user out; display alert from log user out signal
    log_user_logout()

    # Redirect to the landing page
    return redirect("catalog:index")
