# Generated by Django 5.1.2 on 2024-11-09 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_budget_last_reset_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
