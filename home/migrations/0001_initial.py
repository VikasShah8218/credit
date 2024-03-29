# Generated by Django 5.0.1 on 2024-01-22 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('age', models.IntegerField(null=True)),
                ('monthly_income', models.IntegerField(null=True)),
                ('approved_limit', models.BigIntegerField(null=True)),
                ('phone_number', models.BigIntegerField(null=True, unique=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'customer',
            },
        ),
    ]
