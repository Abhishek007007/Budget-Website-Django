# Generated by Django 5.1.2 on 2024-11-09 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_alter_billreminder_recurring_interval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billreminder',
            name='category',
            field=models.CharField(max_length=50),
        ),
    ]
