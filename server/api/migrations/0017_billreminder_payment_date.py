# Generated by Django 5.1.2 on 2024-11-09 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_alter_billreminder_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='billreminder',
            name='payment_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]