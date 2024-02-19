# Generated by Django 4.2.2 on 2024-01-11 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('employeeid', models.IntegerField()),
                ('logintime', models.DateTimeField(null=True)),
                ('logofftime', models.DateTimeField(null=True)),
                ('totalbreakTimex', models.CharField(max_length=100)),
                ('totalmeetingTimex', models.CharField(max_length=100)),
                ('totaldownTimex', models.CharField(max_length=100)),
                ('totalworkx', models.CharField(max_length=100, null=True)),
                ('created', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='LeaveModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('employeeid', models.PositiveIntegerField()),
                ('leaveType', models.CharField(choices=[('Half Day', 'Half Day'), ('Full Day', 'Full Day')], max_length=10)),
                ('halfDayDate', models.DateField(blank=True, null=True)),
                ('fromdate', models.DateField(blank=True, null=True)),
                ('todate', models.DateField(blank=True, null=True)),
                ('reason', models.TextField()),
                ('status', models.CharField(default='Pending', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='regmodel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('employeeid', models.IntegerField()),
                ('designation', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('bloodgroup', models.CharField(max_length=10)),
                ('phonenumber', models.IntegerField()),
                ('dateofbirth', models.CharField(max_length=30)),
                ('joiningdate', models.CharField(max_length=30)),
                ('image', models.FileField(upload_to='attendance_app/static')),
                ('accountnumber', models.IntegerField()),
                ('bankname', models.CharField(max_length=100)),
                ('branch', models.CharField(max_length=30)),
                ('ifsccode', models.IntegerField()),
                ('salary', models.IntegerField()),
                ('password', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='WeekoffModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('employeeid', models.IntegerField()),
                ('weekoff1', models.DateField(blank=True, null=True)),
                ('weekoff2', models.DateField(blank=True, null=True)),
            ],
        ),
    ]