from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, Expense
from django.contrib.auth import authenticate
from .serializers import ExpenseSerializer
import re
from datetime import timedelta, date



def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append('Your password must be more than 8 characters')
    if not re.search(r'[A-Z]', password):
        errors.append('Your password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        errors.append('Your password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        errors.append('Your password must contain at least a number')
    return errors

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({'error':'All fields are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not validate_email(email):
            return Response({'error':'Invalid email format'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        password_errors = validate_password(password)
        if password_errors:
            return Response({'errors':password_errors}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username= username).exists():
            return Response({'error':'Username already exists'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error':'Email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username= username, password=password, email= email)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access":str(refresh.access_token),
            'refresh':str(refresh)
        }, status=status.HTTP_201_CREATED)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username = username, password= password)
        if not user:
            return Response({'error':'Invalid Credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            "access":str(refresh.access_token),
            'refresh':str(refresh)
        })
    
class ExpenseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = Expense.objects.filter(user = request.user)
        filter_param = request.query_params.get('filter')
        if filter_param == 'past_week':
            week_ago = date.today() - timedelta(days=7)
            expenses= expenses.filter(date__gte = week_ago)
        
        elif filter_param == 'past_month':
            month_ago = date.today() - timedelta(days=30)
            expenses = expenses.filter(date__gte= month_ago)

        elif filter_param == 'last_3months':
            three_month_ago = date.today() - timedelta(days=90)
            expenses = expenses.filter(date__gte = three_month_ago)

        elif filter_param == 'custom':
            start = request.query_params.get('start')
            end = request.query_params.get('end')
            if not start or not end:
                return Response({
                    'error': 'Provide start and end date for custom filter'
                }, status= status.HTTP_400_BAD_REQUEST)
            expenses = expenses.filter(date__gte= start, date__lte = end)

        category = request.query_params.get('category')
        if category:
            category = category.objects.filter(category=category)
        serializer = ExpenseSerializer(expenses, many= True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ExpenseSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user= request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ExpenseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk, user):
        try:
            return Expense.objects.get(pk=pk, user= user)
        except Expense.DoesNotExist:
            return None
        
    def get(self, request, pk):
        expenses = self.get_objects(pk, request.user)
        if not expenses: 
            return Response({'error':'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExpenseSerializer(expenses)
        return Response(serializer.data)
    
    def put(self, request, pk):
        expenses = self.get_objects(pk, request.user)
        if not expenses:
            return Response({'error':'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ExpenseSerializer(expenses, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        expenses = self.get_objects(pk, request.user)
        if not expenses: 
            return Response({'error':'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
        expenses.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


        
            
