# Generated by Django 4.2.2 on 2024-02-17 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0035_remove_regmodel_checkin_remove_regmodel_checkout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regmodel',
            name='dateofbirth',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='regmodel',
            name='joiningdate',
            field=models.DateField(),
        ),
    ]
