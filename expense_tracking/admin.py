from django.contrib import admin
from .models import ExpenseType, Expense, Budget


admin.site.register(ExpenseType)
admin.site.register(Expense)
admin.site.register(Budget)
