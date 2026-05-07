from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('expense/', views.ExpenseListView.as_view(), name='expense-list'),
    path('expense/<int:pk>/',views.ExpenseDetailView.as_view(), name='expense-detail')
]