from django.db import models
from django.contrib.auth.models import User
from datetime import date

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
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FinancialGoals(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(decimal_places=2, max_digits=15, default=0.00)
    current_amount = models.DecimalField(decimal_places=2, max_digits=15, default=0.00)
    allocated_amount = models.DecimalField(decimal_places=2, max_digits=15, default=0.00)
    target_date = models.DateField()
    recurrence = models.CharField(max_length=10, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], blank=True)
    income_source = models.ForeignKey(IncomeSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FinancialGoalContribution(models.Model):
    goal = models.ForeignKey(FinancialGoals, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} contributed {self.amount} to {self.goal.name}"


#Group

class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_members')
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('group', 'user') 


class GroupExpense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_expenses')
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class GroupExpenseContribution(models.Model):
    group_expense = models.ForeignKey(GroupExpense, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} contributed {self.amount} to {self.group_expense.title}"


class GroupFinancialGoal(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete= models.CASCADE,null=True, blank=True)

    def __str__(self):
        return self.name


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=100)  # e.g., "Monthly Budget"
    description = models.TextField(blank=True)
    period = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reset_date = models.DateField(default=date.today, blank=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def calculate_balance(self):
        return self.total_income - self.total_expenses

    def add_income(self, amount):
        self.total_income += amount
        self.save()

    def add_expense(self, amount):
        self.total_expenses += amount
        self.save()

    def is_over_budget(self):
        return self.total_expenses > self.budget_limit

    def reset_budget(self):
        self.total_income = 0
        self.total_expenses = 0
        self.save()

    def update_reset_date(self):
        self.last_reset_date = date.today()
        self.save()


from datetime import timedelta


class BillReminder(models.Model):

    RECURRING_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One-Time'),
    ]

    bill_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    due_date = models.DateField()  # Initial due date
    recurring_interval = models.CharField(max_length=20, choices=RECURRING_CHOICES, default='monthly')
    reminder_time = models.IntegerField(help_text="Time in days before due date to send reminder")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)  # Tracks when the bill was paid

    def __str__(self):
        return f"{self.bill_name} due on {self.due_date}"

    def get_next_due_date(self):
        """
        Returns the next due date for the recurring bill based on the current due date and the recurring interval.
        """
        next_due_date = self.due_date
        if self.recurring_interval == 'monthly':
            next_due_date = next_due_date.replace(month=next_due_date.month % 12 + 1)
        elif self.recurring_interval == 'quarterly':
            next_due_date = next_due_date.replace(month=((next_due_date.month - 1) // 3 + 1) * 3 + 1)
        elif self.recurring_interval == 'weekly':
            next_due_date += timedelta(weeks=1)
        elif self.recurring_interval == 'yearly':
            next_due_date = next_due_date.replace(year=next_due_date.year + 1)
        return next_due_date

    def create_recurring_bill(self):
        """
        Creates a new recurring bill for the next due date without marking it as paid.
        """
        next_due_date = self.get_next_due_date()
        BillReminder.objects.create(
            user=self.user,
            bill_name=self.bill_name,
            amount=self.amount,
            category=self.category,
            due_date=next_due_date,
            recurring_interval=self.recurring_interval,
            reminder_time=self.reminder_time,
            is_paid=False
        )

    class Meta:
        ordering = ['due_date']
