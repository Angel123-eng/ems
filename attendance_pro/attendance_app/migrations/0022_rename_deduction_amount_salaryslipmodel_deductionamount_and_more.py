# Generated by Django 4.2.2 on 2024-02-15 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0021_salaryslipmodel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salaryslipmodel',
            old_name='deduction_amount',
            new_name='deductionamount',
        ),
        migrations.RenameField(
            model_name='salaryslipmodel',
            old_name='monthly_salary',
            new_name='monthlysalary',
        ),
        migrations.RenameField(
            model_name='salaryslipmodel',
            old_name='salary_deducted_leave',
            new_name='salarydeducted_leave',
        ),
        migrations.RenameField(
            model_name='salaryslipmodel',
            old_name='total_working_days',
            new_name='totalworkingdays',
        ),
    ]