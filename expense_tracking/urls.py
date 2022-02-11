from django.urls import path
from . import views


app_name = "expense_tracking"

urlpatterns = [
    path('', views.expenses, name="expenses"),
    path('add/', views.add_expense, name="add_expense"),
    path(
        "delete_expense/<int:id>",
        views.delete_expense,
        name='delete_expense'
    ),
]
