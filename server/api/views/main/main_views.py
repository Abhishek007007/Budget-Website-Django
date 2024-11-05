from rest_framework import viewsets
from rest_framework.response import Response
from ...models import IncomeSource, Income, Category, Expense, FinancialGoals, Group, GroupMember, GroupExpense, FinancialGoalContribution
from .serializer import IncomeSourceSerializer, IncomeSerializer, CatagorySerilaizer, ExpenseSerializer, FinancialGoalSerializer, ManualContributionSerializer, GroupSerializer, AddMemberSerializer, GroupExpenseSerializer, GroupExpenseContributionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from itertools import chain
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import serializers

class IncomeSourceView(viewsets.ModelViewSet):
    queryset = IncomeSource.objects.all()
    serializer_class = IncomeSourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return IncomeSource.objects.filter(user=self.request.user)

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
        serializer.save(user=self.request.user)


class CategoryView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CatagorySerilaizer

    def get_queryset(self):
        return Category.objects.filter(user = self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class ExpenseView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user = self.request.user)
    
    def perform_create(self, serializer):
        category = serializer.validated_data.get('category')
        if category.user != self.request.user:
            raise serializers.ValidationError("You can only add expense to your own categories.")
        serializer.save(user = self.request.user)
    

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
        return FinancialGoals.objects.filter(user = self.request.user)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

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
            
  
            goal.current_amount += amount
            goal.save()

            FinancialGoalContribution.objects.create(goal=goal, user=request.user, amount=amount)

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

    @action(detail=True, methods=['DELETE'], url_path='delete-member')
    def delete_member(self, request, pk=None):
        group = self.get_object()
        if group.admin != request.user:
            return Response({"error": "Only the group admin can delete members."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddMemberSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']  
            try:
                member = GroupMember.objects.get(group=group, user__username=username)  
                member.delete()
                return Response({'status': 'Member deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except GroupMember.DoesNotExist:
                return Response({'error': 'User is not a member of this group!'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = GroupExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupExpense.objects.all()

    def perform_create(self, serializer):
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
