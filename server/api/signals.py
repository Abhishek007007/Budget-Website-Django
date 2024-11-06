# api/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.timezone import localdate
from .models import Budget

@receiver(post_migrate)  
def reset_budgets_for_new_day(sender, **kwargs):
    today = localdate()

   
    budgets = Budget.objects.filter(last_reset_date__lt=today)

    for budget in budgets:
       
        budget.reset_budget()

        budget.update_reset_date()
