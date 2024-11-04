from rest_framework import serializers
from ...models import IncomeSource, Income, Category, Expense, FinancialGoals, Group, GroupExpense, GroupFinancialGoal, GroupMember
from datetime import date
from django.contrib.auth.models import User

class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        fields = ['id', 'source_name', 'created_at', 'updated_at'] 
        read_only_fields = ['created_at', 'updated_at']

class IncomeSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=IncomeSource.objects.all()) 
    class Meta:
        model = Income
        fields = ['id', 'user', 'source', 'amount', 'description', 'date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CatagorySerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at', 'user']
        read_only_fields = ['created_at', 'updated_at',  'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ExpenseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Expense
        fields = ['id', 'user', 'category', 'amount', 'description', 'date', 'created_at' , 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TransactionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()  
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
    date = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class FinancialGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialGoals
        fields = ['id', 'user', 'name', 'description', 'target_amount', 'current_amount', 'allocated_amount', 'target_date', 'recurrence', 'income_source', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        if attrs['target_amount'] < attrs['current_amount']:
            raise serializers.ValidationError("Target amount cannot be less than the current amount.")
        if attrs['allocated_amount'] < 0:
            raise serializers.ValidationError("Allocated amount cannot be negative.")
        if attrs['target_date'] < date.today():
            raise serializers.ValidationError("Target date cannot be in the past.")
        return attrs

    
class ManualContributionSerializer(serializers.Serializer):
    goal_id = serializers.IntegerField() 
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)  

    def validate(self, attrs):
        if attrs['amount'] <= 0:
            raise serializers.ValidationError("The amount must be greater than zero.")
        return attrs

class AddMemberSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

    def save(self, group):
        username = self.validated_data['username']
        user = User.objects.get(username=username)

        if GroupMember.objects.filter(group=group, user=user).exists():
            raise serializers.ValidationError("User is already a member of this group.")
        
        GroupMember.objects.create(group=group, user=user)

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['id', 'user', 'joined_at'] 

class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(many=True, read_only=True) 
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'admin', 'members']
        read_only_fields = ['id', 'created_at', 'updated_at', 'admin']

    def create(self, validated_data):
        user = self.context['request'].user
        group = Group.objects.create(admin=user, **validated_data)
        GroupMember.objects.create(group=group, user=user)  
        return group
