from rest_framework import viewsets
from rest_framework.response import Response
from ...models import IncomeSource, Income, Category, Expense, FinancialGoals, Group, GroupMember, GroupExpense, FinancialGoalContribution, Budget
from .serializer import IncomeSourceSerializer, IncomeSerializer, CatagorySerilaizer, ExpenseSerializer, FinancialGoalSerializer, ManualContributionSerializer, GroupSerializer, AddMemberSerializer, GroupExpenseSerializer, GroupExpenseContributionSerializer, BudgetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from itertools import chain
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import serializers
from django.utils.timezone import localdate
from decimal import Decimal
from datetime import date
from django.utils.timezone import localdate

class IncomeSourceView(viewsets.ModelViewSet):
    queryset = IncomeSource.objects.all()
    serializer_class = IncomeSourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)



class CategoryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CatagorySerilaizer

    def get_queryset(self):
        return Category.objects.filter(user = self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


class IncomeView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        source = serializer.validated_data.get('source')
        if source.user != self.request.user:
            raise serializers.ValidationError("You can only add income to your own sources.")
        
        # Check if the user has a budget
        try:
            budget = Budget.objects.get(user=self.request.user)
        except Budget.DoesNotExist:
            # If no budget is found, just save the income without modifying the budget
            serializer.save(user=self.request.user)
            return

        # If budget exists, update the total_income
        amount = serializer.validated_data.get('amount')  # Get amount from validated data
        budget.total_income += amount
        budget.save()

        # Save the income after updating the budget
        serializer.save(user=self.request.user)


class ExpenseView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        category = serializer.validated_data.get('category')
        if category.user != self.request.user:
            raise serializers.ValidationError("You can only add expenses to your own categories.")

        # Check if the user has a budget
        try:
            budget = Budget.objects.get(user=self.request.user)
        except Budget.DoesNotExist:
            # If no budget is found, just save the expense without modifying the budget
            serializer.save(user=self.request.user)
            return

        # Only update today's budget if the expense date is today
        amount = serializer.validated_data.get('amount')
        expense_date = serializer.validated_data.get('date', localdate())  # Default to today if date is not provided
        if expense_date == localdate():
            budget.total_expenses += Decimal(amount)
            budget.save()

        # Save the expense after updating the budget
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Get the original expense amount and date before updating
        original_expense = self.get_object()
        original_amount = original_expense.amount
        original_date = original_expense.date

        # Update the expense
        updated_expense = serializer.save(user=self.request.user)
        new_amount = updated_expense.amount
        new_date = updated_expense.date

        # Adjust the budget only if the expense date matches today
        budget = Budget.objects.get(user=self.request.user)
        today = localdate()
        
        if original_date == today:
            budget.total_expenses -= Decimal(original_amount)
        if new_date == today:
            budget.total_expenses += Decimal(new_amount)

        budget.save()

    def perform_destroy(self, instance):
        # Adjust the budget's total expenses only if the expense date is today
        budget = Budget.objects.get(user=self.request.user)
        if instance.date == localdate():
            budget.total_expenses -= Decimal(instance.amount)
            budget.save()

        # Delete the expense
        instance.delete()


class TransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        incomes = Income.objects.filter(user=request.user).order_by('created_at')
        expenses = Expense.objects.filter(user=request.user).order_by('created_at')

        income_data = IncomeSerializer(incomes, many=True).data
        expense_data = ExpenseSerializer(expenses, many=True).data


        for item in income_data:
            item['type'] = 'income'
        for item in expense_data:
            item['type'] = 'expense'

        combined_data = list(chain(income_data, expense_data))
        sorted_combined_data = sorted(combined_data, key=lambda x: x['created_at'])

        return Response(sorted_combined_data)



class FinancialGoalView(viewsets.ModelViewSet):
    queryset = FinancialGoals.objects.all()
    serializer_class = FinancialGoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FinancialGoals.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Get the updated goal instance
        goal = serializer.save(user=self.request.user)

        # Get the contribution amount from the updated goal (use your logic to get this value)
        contribution_amount = goal.current_amount  # Assuming current_amount is the contribution amount

        # Check if the "Goals" category exists, otherwise create it
        category, created = Category.objects.get_or_create(name="Goals", user=self.request.user)

        # Prepare the expense data
        expense_data = {
            "user": self.request.user,
            "amount": contribution_amount,  # Contribution as the expense amount
            "date": date.today(),  # Set to today's date, can be customized
            "category": category,  # Link the "Goals" category to this expense
            "description": f"Contribution to Goal: {goal.name}",  # Description for the expense
        }

        # Create and save the expense
        expense = Expense.objects.create(**expense_data)

        # Optionally update the user's budget if necessary
        try:
            budget = Budget.objects.get(user=self.request.user)
            budget.total_expenses += Decimal(contribution_amount)
            budget.save()
        except Budget.DoesNotExist:
            pass  # Handle the case where the budget doesn't exist

        # Return the updated financial goal data
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManualContributionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ManualContributionSerializer(data=request.data)
        if serializer.is_valid():
            goal_id = serializer.validated_data['goal_id']
            amount = serializer.validated_data['amount']

            try:
                goal = FinancialGoals.objects.get(id=goal_id, user=request.user)
            except FinancialGoals.DoesNotExist:
                return Response({'error': 'Financial goal not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Update the financial goal's current amount
            goal.current_amount += amount
            goal.save()

            # Create a contribution record
            FinancialGoalContribution.objects.create(goal=goal, user=request.user, amount=amount)

            # Create an expense record for the contribution
            expense_data = {
                "user": request.user,
                "amount": amount,
                "date": localdate(),  # Use today's date
                "category": goal.category,  # Assuming the goal has a related category
                "description": f"Contribution to Goal: {goal.name}",
            }

            # Create and save the expense
            Expense.objects.create(**expense_data)

            # Optionally update the user's budget if necessary
            try:
                budget = Budget.objects.get(user=request.user)
                if expense_data["date"] == localdate():
                    budget.total_expenses += Decimal(amount)
                    budget.save()
            except Budget.DoesNotExist:
                pass  # If no budget exists, do nothing

            return Response({'success': True, 'current_amount': goal.current_amount}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['POST'], url_path='add-member')
    def add_member(self, request, pk=None):
        group = self.get_object()
        if group.admin != request.user:
            return Response({"error": "Only the group admin can add members."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(group=group)
            return Response({"status": "Member added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'], url_path='delete-member/(?P<username>[^/.]+)')
    def delete_member(self, request, pk=None, username=None):
        print(f"Username to delete: {username}")
        group = self.get_object()
       
        # Try to find the member to delete
        try:
            member = GroupMember.objects.get(group=group, user__username=username)
            member.delete()
            return Response({'status': 'Member deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except GroupMember.DoesNotExist:
            return Response({'error': 'User is not a member of this group!'}, status=status.HTTP_404_NOT_FOUND)


class GroupExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = GroupExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupExpense.objects.all()

    def perform_create(self, serializer):
        print(self.request.data)
        group_id = self.request.data.get('group')
    
        if group_id:
            try:
                group = Group.objects.get(pk=group_id)
                serializer.save(group=group, user=self.request.user)
            except Group.DoesNotExist:
                raise serializers.ValidationError({"error": "Group not found."})
        else:
            raise serializers.ValidationError({"error": "Group ID is required."})

    @action(detail=True, methods=['post'], url_path='add-contribution')
    def add_contribution(self, request, pk=None):

        serializer = GroupExpenseContributionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        # Get the current date
        today = localdate()
        user = self.request.user

        # Get the latest budget for the user
        last_budget = Budget.objects.filter(user=user).last()

        # If the last reset date is not today's date, reset the budget
        if last_budget and last_budget.last_reset_date != today:
            self.reset_budget_for_new_day(user, today)

        # Return the budgets for the user
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Get the current date
        today = localdate()
        user = self.request.user

        # Save the new budget with today's reset date
        serializer.save(user=user, last_reset_date=today)

    def reset_budget_for_new_day(self, user, today):
        # This method resets the budget for the user if the day has changed
        # Get all the budgets for the user where last_reset_date is not today
        budgets = Budget.objects.filter(user=user, last_reset_date__lt=today)

        for budget in budgets:
            # Reset the budget's income and expenses
            self.reset_budget(budget)
            # Update the reset date to today
            budget.last_reset_date = today
            budget.save()

    def reset_budget(self, budget):
        # Custom logic to reset the budget (e.g., reset income and expenses)
        budget.total_income = 0
        budget.total_expenses = 0
        budget.save()
