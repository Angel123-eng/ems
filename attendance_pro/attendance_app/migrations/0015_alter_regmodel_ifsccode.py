# Generated by Django 4.2.2 on 2024-03-27 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0014_alter_regmodel_ifsccode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regmodel',
            name='ifsccode',
            field=models.CharField(max_length=30),
        ),
    ]