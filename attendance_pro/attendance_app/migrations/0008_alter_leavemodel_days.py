# Generated by Django 4.2.2 on 2024-01-14 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0007_leavemodel_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavemodel',
            name='days',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
