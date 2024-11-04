from rest_framework import viewsets
from rest_framework.response import Response
from ...models import IncomeSource, Income, Category, Expense, FinancialGoals, Group, GroupMember
from .serializer import IncomeSourceSerializer, IncomeSerializer, CatagorySerilaizer, ExpenseSerializer, FinancialGoalSerializer, ManualContributionSerializer, GroupSerializer, AddMemberSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from itertools import chain
from rest_framework import status
from rest_framework.decorators import action



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

            return Response({'success': True, 'current_amount': goal.current_amount}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        group = self.get_object()
        if group.admin != request.user:
            return Response({"error": "Only the group admin can add members."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AddMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(group=group)
            return Response({"status": "Member added successfully"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





    