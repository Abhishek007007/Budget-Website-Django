# Generated by Django 5.1.2 on 2024-11-04 04:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_expense_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FianacialGoals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('target_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('current_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('allocated_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=15)),
                ('target_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_goals', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
