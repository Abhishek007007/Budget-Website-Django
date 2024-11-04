from celery import shared_task
from .models import FinancialGoals, Income
from django.db.models import F

@shared_task
def transfer_to_financial_goals():
    goals = FinancialGoals.objects.filter(current_amount__lt=F('target_amount'), recurring=True)
    def calculate_transfer_amount(goal):
        if goal.recurrence == 'daily':
            return goal.allocated_amount  
        elif goal.recurrence == 'weekly':
            return goal.allocated_amount * 7  
        elif goal.recurrence == 'monthly':
            return goal.allocated_amount * 30  
        return 0  

    for goal in goals:
       
        transfer_amount = calculate_transfer_amount(goal) 
        income = Income.objects.filter(source=goal.income_source, user=goal.user).first()
        

        if income and income.amount >= transfer_amount:
       
            income.amount -= transfer_amount
            income.save()
            
       
            goal.current_amount += transfer_amount
            goal.save()
    
