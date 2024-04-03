from django.contrib import admin
from .models import regmodel,LeaveModel,AttendanceModel,WeekoffModel,PublicholidaysModel,ExtraModel,ExcelModel,SalarySlipModel,ProductivityModel
# Register your models here.

class regAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','designation','email','bloodgroup','phonenumber','dateofbirth','joiningdate','image','accountnumber','bankname','branch','ifsccode','salary','password','status','logintime', 'address')
 
class leaveAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','leaveType', 'halfDayDate','fromdate','todate','reason','status','days','applieddate')
    
class AttendanceAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','logintime','logofftime','totalbreakTimex','totalmeetingTimex','totaldownTimex','totalworkx','status','created')
    
class WeekoffAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','weekoff1','weekoff2') 
    
class PublicholidaysAdmin(admin.ModelAdmin):
    list_display=('date','status') 
    
class ExtraAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','date','status','login')

class ExcelModelAdmin(admin.ModelAdmin):
    list_display = ('employeeid', 'name', 'date', 'intime', 'outtime')  # Add intime and outtime to the list_display

class SalarySlipModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'employeeid', 'month', 'year', 'totalPayableDays', 'totalleave', 'paidleave','Latelogin', 'salarydeductedleave', 'salary', 'perdaysalary', 'deductionamount', 'incentive', 'monthlysalary')

class ProductivityModelAdmin(admin.ModelAdmin):
    list_display = ('employeeid', 'month', 'productivity', 'quality', 'appreciations','extraInitiatives','target','achievement','percentage','newClient','renewals')

admin.site.register(regmodel, regAdmin)
admin.site.register(LeaveModel, leaveAdmin)
admin.site.register(AttendanceModel, AttendanceAdmin)
admin.site.register(WeekoffModel,WeekoffAdmin)
admin.site.register(PublicholidaysModel, PublicholidaysAdmin)
admin.site.register(ExtraModel, ExtraAdmin)
admin.site.register(ExcelModel,ExcelModelAdmin)
admin.site.register(SalarySlipModel, SalarySlipModelAdmin)
admin.site.register(ProductivityModel,ProductivityModelAdmin)
