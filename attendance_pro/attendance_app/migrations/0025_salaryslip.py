# Generated by Django 4.2.2 on 2024-02-15 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0024_delete_salaryslipmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalarySlip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('employee_id', models.CharField(max_length=20)),
                ('month', models.CharField(max_length=20)),
                ('year', models.IntegerField()),
                ('totalworkingdays', models.IntegerField()),
                ('salarydeductedleave', models.IntegerField()),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('deductionamount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monthlysalary', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]