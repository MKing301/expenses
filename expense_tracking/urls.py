from django.urls import path
from . import views


app_name = "expense_tracking"

urlpatterns = [
    path('', views.expenses, name="expenses"),
]
