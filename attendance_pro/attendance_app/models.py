from django.db import models
from django.utils import timezone


# Create your models here.

class regmodel(models.Model):
    name=models.CharField(max_length=30)
    employeeid=models.CharField(max_length=30)
    designation=models.CharField(max_length=30)
    email=models.EmailField()
    bloodgroup=models.CharField(max_length=10)
    phonenumber=models.IntegerField()
    dateofbirth=models.CharField(max_length=30)
    joiningdate=models.CharField(max_length=30)
    image=models.FileField(upload_to='attendance_app/static')
    accountnumber=models.CharField(max_length=30)
    bankname=models.CharField(max_length=100)
    branch=models.CharField(max_length=30)
    ifsccode=models.CharField(max_length=30)
    salary=models.IntegerField()
    password=models.CharField(max_length=10)
    status = models.CharField(max_length=20, default='Active')
    logintime = models.CharField(max_length=20)
    address = models.CharField(max_length=1000)

class LeaveModel(models.Model):
    name = models.CharField(max_length=255)
    employeeid = models.CharField(max_length=30)
    leaveType = models.CharField(max_length=10, choices=[('Half Day', 'Half Day'), ('Full Day', 'Full Day')])
    halfDayDate = models.DateField(blank=True, null=True)
    fromdate = models.DateField(blank=True, null=True)
    todate = models.DateField(blank=True, null=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, default='Pending')
    days=models.DecimalField(max_digits=5, decimal_places=1, default=0.0)# Adjust max_digits and decimal_places as needed
    applieddate=models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.employeeid} - {self.leaveType}"
    

class AttendanceModel(models.Model):
    name = models.CharField(max_length=30)
    employeeid = models.CharField(max_length=30)
    logintime = models.DateTimeField(null=True)
    logofftime = models.DateTimeField(null=True)
    totalbreakTimex = models.CharField(max_length=100)  # Adjust the max length as needed
    totalmeetingTimex = models.CharField(max_length=100)
    totaldownTimex = models.CharField(max_length=100)
    totalworkx = models.CharField(max_length=100, null=True)
    status=models.CharField(max_length=30)
    created = models.DateTimeField()
    
def __str__(self):
        return f"{self.logintime} - {self.logofftime}"
    
    
class WeekoffModel(models.Model):
    name = models.CharField(max_length=30)
    employeeid = models.CharField(max_length=30)
    weekoff1 = models.DateField(blank=True, null=True)
    weekoff2 = models.DateField(blank=True, null=True)
    
class PublicholidaysModel(models.Model):
    date=models.DateField(blank=True, null=True)
    status=models.CharField(max_length=40)
    
class ExtraModel(models.Model):
    name=models.CharField(max_length=30)
    employeeid=models.CharField(max_length=30)
    date=models.DateField(blank=True, null=True)
    status=models.CharField(max_length=40)
    login=models.CharField(max_length=20)


from django.db import models

class ExcelModel(models.Model):
    employeeid = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    date = models.DateField()
    intime = models.TimeField()  # Add intime field
    outtime = models.TimeField()  # Add outtime field

    def __str__(self):
        return f"{self.employeeid} - {self.name}"
    
# models.py

from django.db import models

class SalarySlipModel(models.Model):
    name = models.CharField(max_length=30)
    employeeid= models.CharField(max_length=20)
    month = models.CharField(max_length=30)
    year = models.IntegerField()
    totalPayableDays  = models.DecimalField(max_digits=10, decimal_places=1)
    totalleave = models.DecimalField(max_digits=10, decimal_places=1)
    paidleave = models.DecimalField(max_digits=10, decimal_places=1)
    Latelogin = models.DecimalField(max_digits=10, decimal_places=1)
    salarydeductedleave = models.DecimalField(max_digits=10, decimal_places=1)
    salary = models.DecimalField(max_digits=10, decimal_places=3)
    perdaysalary = models.DecimalField(max_digits=10, decimal_places=3)
    deductionamount = models.DecimalField(max_digits=10, decimal_places=3)
    incentive = models.DecimalField(max_digits=10, decimal_places=3)
    monthlysalary = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.name} - {self.month} {self.year} Salary Slip"
    
    
from django.db import models

from django.db import models

class ProductivityModel(models.Model):
    name = models.CharField(max_length=30)
    employeeid = models.CharField(max_length=20)
    month = models.CharField(max_length=30)
    productivity = models.DecimalField(max_digits=10, decimal_places=2)
    quality = models.DecimalField(max_digits=10, decimal_places=2)
    appreciations = models.IntegerField()
    extraInitiatives = models.IntegerField()
    target = models.DecimalField(max_digits=10, decimal_places=2)
    achievement = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=10, decimal_places=2)
    newClient = models.CharField(max_length=50)
    renewals = models.DecimalField(max_digits=10, decimal_places=2)


    



    