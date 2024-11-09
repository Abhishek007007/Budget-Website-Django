# Generated by Django 5.1.2 on 2024-11-09 08:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_expense_date_alter_income_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_name', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.CharField(choices=[('electricity', 'Electricity'), ('water', 'Water'), ('internet', 'Internet'), ('subscription', 'Subscription'), ('other', 'Other')], max_length=50)),
                ('due_date', models.DateField()),
                ('recurring_interval', models.CharField(choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly'), ('one_time', 'One-Time')], default='monthly', max_length=20)),
                ('reminder_time', models.IntegerField(help_text='Time in days before due date to send reminder')),
                ('is_paid', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['due_date'],
            },
        ),
    ]
