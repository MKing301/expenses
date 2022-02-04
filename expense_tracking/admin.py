from django.contrib import admin
from .models import ExpenseType, Expense


admin.site.register(ExpenseType)
admin.site.register(Expense)
