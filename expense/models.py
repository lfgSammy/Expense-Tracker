from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    
class Expense(models.Model):
    CATEGORY_CHOICES = [
    ('food', 'Food'),
    ('groceries', 'Groceries'),
    ('leisure', 'Leisure'),
    ('electronics', 'Electronics'),
    ('utilities', 'Utilities'),
    ('clothing', 'Clothing'),
    ('health', 'Health'),
    ('others', 'Others'),
]    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=15, default=1)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='others')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank= True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.category} - {self.amount}'