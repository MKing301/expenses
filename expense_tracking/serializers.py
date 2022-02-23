from rest_framework import serializers
from .models import ExpenseType


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = ('id', 'name')
