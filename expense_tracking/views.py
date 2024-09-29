from locale import currency
import pandas as pd
import pandasql as ps
import numpy as np
import plotly.graph_objs as go
import logging


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Expense, ExpenseType, Budget
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
pd.set_option('future.no_silent_downcasting', True)

logger = logging.getLogger(__name__)

class ExpenseTypeView(viewsets.ModelViewSet):
    # Class for expense type view set

    # Select all expense types
    queryset = ExpenseType.objects.all().order_by('name')

    # Serialize class
    serializer_class = ExpenseTypeSerializer


def get_chart(category, title):

    df = category
    trace1 = go.Bar(
                x=df['Category'],
                y=df['Budget Amount'],
                name='Budget',
                hovertemplate='%{y}',  # Display only the value on hover
                #text=[f'{cat}: {val}' for cat, val in zip(budget['Category'], budget['Total Monthly Balance'])],
                textposition='auto',
                showlegend=True
            )

    trace2 = go.Bar(
        x=df['Category'],
        y=df['Monthly Expense Amount'],
        name='Expense',
        hovertemplate='%{y}',  # Display only the value on hover
        # text=[f'{cat}: {val}' for cat, val in zip(budget['Category'], budget['Monthly Expense Amount'])],
        textposition='auto',
        showlegend=True
    )

    layout = go.Layout(
        title={
            'text': f'<b>{title} Monthly Budget</b>',
        },
        title_x=.5,
        xaxis={
            'title': '<b>Category</b>'
        },
        yaxis={
            'title': '<b>Amount (in dollars)</b>'
        },
        barmode='group',
        height=500,  # Set the height of the chart in pixels
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    fig = go.Figure(data=[trace1, trace2], layout=layout)
    plt_div = plot(fig, output_type='div')
    return plt_div


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
    # log_user_logout()

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
                        },
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
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
def budget(request):

    current = timezone.now()
    current_month_display_name = current.strftime('%b')
    current_month = current.month
    current_year = current.year


    df = pd.DataFrame(list(
                    Expense.objects.all().values(
                        'expense_date',
                        'expense_type__name',
                        'name',
                        'org',
                        'amount',
                        'inserted_date'
                    ).filter(
                        expense_date__year=current_year,
                        expense_date__month=current_month
                        )
                    )
                )

    if len(df.index) == 0:
        return render(
                        request=request,
                        template_name='expense_tracking/budget.html',
                        context={
                            'none': 'No expense records found for this month!',
                        }
                    )

    else:
        # Using as_index=False set the index
        tracking= df.groupby('expense_type__name', as_index=False)['amount'].sum()

        tracking.columns = ['Expense Type', 'Amount']

        budget =  pd.DataFrame(list(
                        Budget.objects.all().values(
                            'name',
                            'beginning_bal',
                            'budget_amt',
                            'total_monthly_bal',
                            'expense_amt',
                            'current_bal'
                        )))

        budget['beginning_bal'] = budget['beginning_bal'].astype(float)
        budget['budget_amt'] = budget['budget_amt'].astype(float)
        budget['total_monthly_bal'] = budget['beginning_bal'] + budget['budget_amt']

        # Merge budget and tracking DataFrames on the matching columns
        merged = pd.merge(budget, tracking, left_on='name', right_on='Expense Type', how='left', suffixes=('', '_tracking'))


        # Update the amount column in budget DataFrame with values from tracking DataFrame
        budget['expense_amt'] = merged['Amount'].combine_first(merged['expense_amt']).astype(float)

        # Replace None with 0
        budget = budget.fillna(0)

        budget['rounded_expense_amt'] = np.ceil(budget['expense_amt'].astype(float))
        budget['current_bal'] = budget['total_monthly_bal'].astype(float) - budget['expense_amt'].astype(float)

        # Rename columns
        budget.columns = ['Category', 'Beginning Balance', 'Budget Amount', 'Total Monthly Balance', 'Monthly Expense Amount', 'Current Monthly Balance', 'Rounded Monthly Expense Amount']

        # Re-order colums
        budget = budget[['Category', 'Beginning Balance', 'Budget Amount', 'Total Monthly Balance', 'Monthly Expense Amount', 'Rounded Monthly Expense Amount', 'Current Monthly Balance']]

        sorted_budget = budget.sort_values(by=['Category'])
        # Convert dataframe to dictionary
        budget_dict = sorted_budget.to_dict(orient='records')


        for data in budget_dict:
            Budget.objects.filter(name=data['Category']).update(
                beginning_bal=data['Beginning Balance'],
                total_monthly_bal=data['Total Monthly Balance'],
                expense_amt=data['Monthly Expense Amount'],
                current_bal=data['Current Monthly Balance']
            )

        # Calculate the sum of numeric columns
        numeric_sum = sorted_budget.select_dtypes(include='number').sum()

        # Convert the numeric sums to a DataFrame with the same columns
        sum_row = pd.DataFrame(numeric_sum).transpose()
        sum_row['Category'] = 'Totals'


        # Append the sum row to the original DataFrame
        df = pd.concat([sorted_budget, sum_row], ignore_index=True)


        food = budget[budget['Category'] == 'Food']
        gas = budget[budget['Category'] == 'Transportation-Gas']
        aquasana = budget[budget['Category'] == 'Aquasana']
        clothing = budget[budget['Category'] == 'Clothing']
        salon = budget[budget['Category'] == 'Salon']
        cleaning = budget[budget['Category'] == 'Dry Cleaning']
        toll = budget[budget['Category'] == 'Transportation-Toll']
        lawn = budget[budget['Category'] == 'Lawn Care']
        personal_care = budget[budget['Category'] == 'Personal Care Items']
        gifts = budget[budget['Category'] == 'Gifts']
        household = budget[budget['Category'] == 'Household Supplies']

        if len(budget.index) == 0:
                        return render(
                            request=request,
                            template_name='expense_tracking/budget.html',
                            context={
                                'current_month_display_name': current_month_display_name,
                                'current_year': current_year,
                                'none': 'No records found!',
                            }
                        )
        else:
            food_chart =get_chart(food, 'Food')
            gas_chart = get_chart(gas, 'Gas')
            aquasana_chart = get_chart(aquasana, 'Aquasana')
            clothing_chart = get_chart(clothing, 'Clothing')
            salon_chart = get_chart(salon, 'Salon')
            cleaning_chart = get_chart(cleaning, 'Cleaning')
            toll_chart = get_chart(toll, 'Toll')
            lawn_chart = get_chart(lawn, 'Lawn')
            personal_care_chart = get_chart(personal_care, 'Personal')
            gifts_chart = get_chart(gifts, 'Gifts')
            household_chart = get_chart(household, 'Household')

            charts = [
                aquasana_chart, clothing_chart, cleaning_chart, food_chart,
                gifts_chart, household_chart, lawn_chart, personal_care_chart,
                salon_chart, gas_chart, toll_chart
            ]
            return render(
                request=request,
                template_name='expense_tracking/budget.html',
                context={
                    'current_month_display_name': current_month_display_name,
                    'current_year': current_year,
                    'budget': build_table(
                                        df, 'blue_light'
                                    ),
                    'charts': charts
                }
            )


@ login_required
def results(request):
    return render(
        request=request,
        template_name='expense_tracking/results.html'
    )
