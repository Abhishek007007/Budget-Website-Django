from django.db import models
from django.contrib.auth.models import User

class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomesource')
    source_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income')
    source = models.ForeignKey(IncomeSource, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FianacialGoals(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(decimal_places=2, max_digits=15, default=0.00)
    current_amount = models.DecimalField(decimal_places=2, max_digits=15, default=0.00)
    allocated_amount = models.DecimalField(decimal_places=2, max_digits=15, default=0.00)
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
