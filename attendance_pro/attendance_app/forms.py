from django import forms
from datetime import datetime

class regform(forms.Form):
    name=forms.CharField(max_length=30)
    employeeid=forms.CharField(max_length=20)
    designation=forms.CharField(max_length=30)
    email=forms.EmailField()
    bloodgroup=forms.CharField(max_length=10)
    phonenumber=forms.IntegerField()
    dateofbirth=forms.DateField(widget=forms.SelectDateWidget)
    joiningdate=forms.DateField(widget=forms.SelectDateWidget)
    image=forms.FileField()
    accountnumber=forms.CharField(max_length=30)
    bankname=forms.CharField(max_length=100)
    branch=forms.CharField(max_length=30)
    ifsccode=forms.CharField(max_length=30)
    salary=forms.IntegerField()
    password=forms.CharField(max_length=30)
    confirmpassword=forms.CharField(max_length=30)
    status =forms.CharField(max_length=20)
    logintime = forms.CharField(max_length=20)
    logintime_sat = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=1000)
    department = forms.CharField(max_length=30)
    shifttime = forms.CharField(max_length=30)
    shifttime_sat = forms.CharField(max_length=30)
    idproof=forms.FileField()
    educationalcertificate=forms.FileField()
    workexperience=forms.FileField()
    resume=forms.FileField()
    others=forms.FileField()
    maritalstatus=forms.CharField(max_length=20)
    gender=forms.CharField(max_length=20)  
     
class adminloginform(forms.Form):
    username=forms.CharField(max_length=20)
    password=forms.CharField(max_length=20)
    
class managerloginform(forms.Form):
    username=forms.CharField(max_length=20)
    password=forms.CharField(max_length=20)
    
        
class logform(forms.Form):
    employeeid=forms.CharField(max_length=20)
    password=forms.CharField(max_length=20)
    

from .models import LeaveModel, AttendanceModel, WeekoffModel, PublicholidaysModel, ExtraModel, ProductivityModel

class LeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveModel
        fields = ['name', 'employeeid', 'leaveType', 'halfDayDate', 'fromdate', 'todate', 'reason','applieddate']

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('fromdate')
        to_date = cleaned_data.get('todate')

        if from_date and to_date and from_date > to_date:
            raise forms.ValidationError("The 'from date' should be before the 'to date'.")
        
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceModel
        exclude = ['created']
        fields = ['name','employeeid','logintime', 'logofftime', 'totalbreakTimex', 'totalmeetingTimex', 'totaldownTimex', 'totalworkx','status']

class WeekoffForm(forms.ModelForm):
    class Meta:
        model=WeekoffModel
        fields=['name','employeeid','weekoff1','weekoff2']
        
class PublicholidaysForm(forms.ModelForm):
    class Meta:
        model=PublicholidaysModel
        fields=['date','status']
        
from django import forms
from .models import ExtraModel

class ExtraForm(forms.ModelForm):
    class Meta:
        model = ExtraModel
        fields = ['name', 'employeeid', 'date', 'status']
       
        
        
# forms.py
from django import forms
from .models import ExtraModel

class ExtraStatusForm(forms.ModelForm):
    class Meta:
        model = ExtraModel
        fields = ['status']

from .models import ExcelModel

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelModel
        fields = ['excel_file']
    
    excel_file = forms.FileField(
        label='Choose an Excel file (.xlsx, .xls)',
        widget=forms.FileInput(attrs={'accept': '.xlsx, .xls', 'required': 'required'})
    )


from django import forms
from .models import SalarySlipModel

class SalarySlipModelForm(forms.ModelForm):
    class Meta:
        model = SalarySlipModel
        fields = '__all__' 

   
 
 
from django import forms
from .models import ProductivityModel

class ProductivityForm(forms.ModelForm):
    class Meta:
        model = ProductivityModel
        fields = ['name', 'employeeid', 'month', 'productivity', 'quality', 'appreciations', 'extraInitiatives', 'target', 'achievement', 'percentage', 'newClient', 'renewals']

    def clean_percentage(self):
        percentage = self.cleaned_data['percentage']
        if percentage < 0 or percentage > 1:
            raise forms.ValidationError("Percentage value must be between 0 and 1.")
        return percentage
    
class DepartmentForm(forms.Form):
    department=forms.CharField(max_length=30)
    

class Managerform(forms.Form):
    department=forms.CharField(max_length=30)
    employeeid=forms.CharField(max_length=30)
    

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(max_length=20, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=20, widget=forms.PasswordInput)

  