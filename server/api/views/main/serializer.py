from rest_framework import serializers
from ...models import IncomeSource, Income, Category, Expense

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