from rest_framework import serializers
from .models import User, Expense

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','created_at']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'user', 'title', 'category','amount','description',
                  'date','created_at','updated_at']
        read_only_fields = ['user','created_at','updated_at']