# Generated by Django 4.2.2 on 2024-03-05 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salaryslipmodel',
            old_name='totalworkingdays',
            new_name='totalpayabledays',
        ),
    ]