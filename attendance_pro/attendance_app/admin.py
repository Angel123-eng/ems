from django.contrib import admin
from .models import regmodel,LeaveModel,AttendanceModel,WeekoffModel,PublicholidaysModel,ExtraModel,SalarySlipModel
# Register your models here.

class regAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','designation','email','bloodgroup','phonenumber','dateofbirth','joiningdate','image','accountnumber','bankname','branch','ifsccode','salary','password','status')
 
class leaveAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','leaveType', 'halfDayDate','fromdate','todate','reason','status','days','applieddate')
    
class AttendanceAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','logintime','logofftime','totalbreakTimex','totalmeetingTimex','totaldownTimex','totalworkx','status','created')
    
class WeekoffAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','weekoff1','weekoff2') 
    
class PublicholidaysAdmin(admin.ModelAdmin):
    list_display=('date','status') 
    
class ExtraAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','date','status')
    
class SalarySlipAdmin(admin.ModelAdmin):
    list_display=('name','employeeid','month','year','totalworkingdays','salarydeductedleave','salary','deductionamount','monthlysalary')
    
    

     
admin.site.register(regmodel, regAdmin)
admin.site.register(LeaveModel, leaveAdmin)
admin.site.register(AttendanceModel, AttendanceAdmin)
admin.site.register(WeekoffModel,WeekoffAdmin)
admin.site.register(PublicholidaysModel, PublicholidaysAdmin)
admin.site.register(ExtraModel, ExtraAdmin)
admin.site.register(SalarySlipModel, SalarySlipAdmin)
