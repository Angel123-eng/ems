# Generated by Django 4.2.2 on 2024-03-23 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salaryslipmodel',
            name='incentive',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salaryslipmodel',
            name='paidleave',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
