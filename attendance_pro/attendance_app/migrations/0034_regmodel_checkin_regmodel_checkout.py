# Generated by Django 4.2.2 on 2024-02-17 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0033_remove_regmodel_checkin_remove_regmodel_checkout'),
    ]

    operations = [
        migrations.AddField(
            model_name='regmodel',
            name='checkin',
            field=models.TimeField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regmodel',
            name='checkout',
            field=models.TimeField(default=1),
            preserve_default=False,
        ),
    ]
