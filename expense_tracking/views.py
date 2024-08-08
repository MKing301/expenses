import pandas as pd
import pandasql as ps
import plotly.graph_objs as go
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, ExpenseType
from .forms import (
    ExpenseForm,
    AuthenticationFormWithCaptchaField,
    DateRangeForm
)
from django.contrib.auth import (
    login, logout, authenticate)
from django.contrib import messages
from .signals import log_user_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework import viewsets
from .serializers import ExpenseTypeSerializer
from pretty_html_table import build_table
from django.utils import timezone
from plotly.offline import plot


# Set float values to 2 decimal places
pd.options.display.float_format = '{:,.2f}'.format

logger = logging.getLogger(__name__)

class ExpenseTypeView(viewsets.ModelViewSet):
    # Class for expense type view set

    # Select all expense types
    queryset = ExpenseType.objects.all().order_by('name')

    # Serialize class
    serializer_class = ExpenseTypeSerializer


def index(request):
    # Function renders landing page

    return render(
        request=request,
        template_name='expense_tracking/index.html',
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
                login_msg = f'{username} logged in successfully.'
                messages.success(
                    request,
                    login_msg
                )
                return redirect('expense_tracking:expenses')

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
                        'Contact the administrator to activate your account!'
                    )
                    return redirect('expense_tracking:login_request')

                # Present form to the user with any errors
                else:
                    return render(
                        request=request,
                        template_name='expense_tracking/login.html',
                        context={'form': form}
                    )

            # Present form to the user with any errors
            else:
                return render(
                    request=request,
                    template_name='expense_tracking/login.html',
                    context={'form': form}
                )

        # When the form is NOT being submitted, present to form to the user
        else:
            form = AuthenticationFormWithCaptchaField()
            return render(
                request=request,
                template_name='expense_tracking/login.html',
                context={'form': form}
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
        return redirect('expense_tracking:expenses')


def password_reset_complete(request):
    return render(
        request=request,
        template_name='accounts/password_reset_complete.html'
    )


@login_required()
def expenses(request):
    # Function requires user to be logged in and renders a table of expenses
    # showing the date, type organization, amount and notes (with edit and
    # delete buttons)

    # Set up pagination
    # Get 50 expenses per page, by expense date descending
    p = Paginator(Expense.objects.order_by(
        '-expense_date',
        'expense_type__name',
        'name',
        'org'
    ), 50)
    page = request.GET.get('page')
    my_expenses = p.get_page(page)

    distinct_expense_types = ExpenseType.objects.all().order_by(
            'name'
            )

    # Render expense table list 50 expense per page with page navigation at
    # the bottom of the page
    return render(request=request,
                  template_name='expense_tracking/expense.html',
                  context={
                      'my_expenses': my_expenses,
                      'distinct_expense_types': distinct_expense_types
                  }
                  )


@login_required()
def add_expense(request):
    # Function for adding an expense.  User must be logged in to access.

    # Obtain expense records ordered by expense name
    expense_types = ExpenseType.objects.order_by('name')

    # When the form method is post
    if request.method == 'POST':

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
                template_name='expense_tracking/add_expense.html',
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
    if request.method == 'POST':
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


@login_required
def filter(request, id):

    # Function requires user to be logged in and renders a table of expenses
    # showing the date, type organization, amount and notes (with edit and
    # delete buttons)

    # Set up pagination
    # Get 50 expenses per page, by expense date descending
    p = Paginator(Expense.objects.filter(expense_type__id=id).order_by(
        '-expense_date',
        'expense_type__name',
        'name',
        'org'
    ), 50)
    page = request.GET.get('page')
    my_expenses = p.get_page(page)

    distinct_expense_types = ExpenseType.objects.all().order_by('name')

    # Render a dropdown list of expense types to filter by, the expense table
    # list with 50 expense per page with page navigation at the bottom of the
    # page
    return render(request=request,
                  template_name='expense_tracking/expense.html',
                  context={
                      'my_expenses': my_expenses,
                      'distinct_expense_types': distinct_expense_types
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
    return redirect('catalog:index')


@login_required()
def get_data(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DateRangeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            start = form.cleaned_data['start_date']
            end = form.cleaned_data['end_date']

            # String format of dates for chart
            start_str = start.strftime('%m-%d-%Y')
            end_str = end.strftime('%m-%d-%Y')

            if ((end - start).days < 0 or (end - start).days > 366):
                return render(
                    request=request,
                    template_name='expense_tracking/get_data.html',
                    context={
                        'form': form
                    }
                )

            else:
                # Create dataframe from all expense records for specified
                # fields
                df = pd.DataFrame(list(
                    Expense.objects.all().values(
                        'expense_date',
                        'expense_type__name',
                        'name',
                        'org',
                        'amount',
                        'inserted_date'
                    )
                )
                )


                # Max date for df
                max_date = df['inserted_date'].max()

                # Convert amount column values to float
                df['amount'] = pd.to_numeric(df['amount'], downcast='float')


                # Select sub-dataframe for date range fromform
                mask = (
                    df['expense_date'] >= start
                ) & (
                    df['expense_date'] <= end
                )

                # Query for df grouped by expense type with sum of amounts for
                # between dates from form
                filtered_df = df[mask]

                # Using as_index=False set the index
                grouped_df= filtered_df.groupby('expense_type__name', as_index=False)['amount'].sum()

                grouped_df.columns = ['Expense Type', 'Amount']

                if len(grouped_df.index) == 0:
                    return render(
                        request=request,
                        template_name='expense_tracking/results.html',
                        context={
                            'none': 'No records found for the specified range!',
                            'start': start,
                            'end': end
                        }
                    )
                else:
                    trace = go.Bar(
                        x=grouped_df['Expense Type'],
                        y=grouped_df['Amount']
                    )

                    layout = go.Layout(
                        title={
                            'text': f'<b>Expenses from {start_str} to {end_str}</b>',
                        },
                        title_x=.5,
                        xaxis={
                            'title': '<b>Expense Type</b>'
                        },
                        yaxis={
                            'title': '<b>Amount (in dollars)</b>'
                        }
                    )
                    fig = go.Figure(data=trace, layout=layout)
                    plt_div = plot(fig, output_type='div')

                    # Display info alert for results with current timestamp
                    messages.info(
                        request,
                        f'''Here are the latest results as of
                        {max_date.strftime(
                        "%m-%d-%Y %I:%M:%S %p %Z"
                        )}.'''
                    )
                    return render(
                        request=request,
                        template_name='expense_tracking/results.html',
                        context={
                            'grouped_df': build_table(
                                grouped_df, 'blue_light'
                            ),
                            'plt_div': plt_div,
                            'start': start,
                            'end': end
                        }
                    )

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DateRangeForm()

    # Render data visualization template for 2021 data
    return render(
        request=request,
        template_name='expense_tracking/get_data.html',
        context={
            'form': form
        }
    )


@ login_required
def results(request):
    return render(
        request=request,
        template_name='expense_tracking/results.html'
    )
