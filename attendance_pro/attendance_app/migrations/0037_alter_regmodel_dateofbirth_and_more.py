# Generated by Django 4.2.2 on 2024-02-17 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0036_alter_regmodel_dateofbirth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regmodel',
            name='dateofbirth',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='regmodel',
            name='joiningdate',
            field=models.CharField(max_length=30),
        ),
    ]
