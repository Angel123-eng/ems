# Generated by Django 4.2.2 on 2024-06-15 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0013_alter_salaryslipmodel_byod_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='regmodel',
            name='shifttime_sat',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
    ]
