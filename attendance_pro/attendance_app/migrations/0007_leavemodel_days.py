# Generated by Django 4.2.2 on 2024-01-14 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0006_remove_leavemodel_num_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavemodel',
            name='days',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
