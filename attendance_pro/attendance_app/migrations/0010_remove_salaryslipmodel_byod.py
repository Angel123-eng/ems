# Generated by Django 4.2.2 on 2024-06-05 10:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0009_salaryslipmodel_byod'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salaryslipmodel',
            name='byod',
        ),
    ]
