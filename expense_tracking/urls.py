from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


app_name = "expense_tracking"

urlpatterns = [
    path('', views.expenses, name="expenses"),
    path('add/', views.add_expense, name="add_expense"),
    path(
        "delete_expense/<int:id>",
        views.delete_expense,
        name='delete_expense'
    ),
    path("login/", views.login_request, name="login_request"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
]
