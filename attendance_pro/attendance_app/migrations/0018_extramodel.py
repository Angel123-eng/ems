# Generated by Django 4.2.2 on 2024-01-29 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0017_delete_employeemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('employeeid', models.IntegerField()),
                ('date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(max_length=40)),
            ],
        ),
    ]
