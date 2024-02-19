from django.urls import path
from . import views 
from .views import *
from .views import handle_frontend_data
from django.urls import path
from .views import display_attendance


urlpatterns=[
    path('',views.signin),
    path('admindashboard/',views.admindashboard),
    path('adminlogin/',views.adminlogin),
    path('adminlogout/', adminlogout, name='adminlogout'),
    # path('attendance/',views.attendance),
    # path('employeedashboard/',views.employeedashboard),
    path('attendancesalary/<int:employeeId>/', views.attendance_salary_view, name='attendancesalary'),
    path('employeedetails/',views.employeedetails),
    path('editemployeedetails/<int:id>',views.editemployeedetails),
    path('leave/<int:id>',views.leave),
    path('monthlyattendance/',views.monthlyattendance),
    path('register/',views.register),
    # path('leaveapplication/',views.leaveapplication),
    # path('profile/',views.profile),
    path('signin/',views.signin),
    path('signout/', signout, name='signout'),    
    path('tasks/',views.tasks),
    # path('salary/',views.salary),
    # path('salaryslip/',views.salaryslip),
    path('leavedisplay/',views.leavedisplay),
    # path('latestleave/',views.latestleave),
    path('leavestatus/',views.leavestatus),
    path('base/', base, name='base'),
    path('dashboard/', page2, name='page2'),
    path('profilex/',page3,name='page3'),
    path('attendancex/',page4, name='page4'),
    path('leaveapplicationx/',page5, name='page5'),
    path('salaryx/',page6, name='page6'),
    path('logentry', handle_frontend_data, name='handle_frontend_data'),
    path('display_attendance/', display_attendance, name='display_attendance'),
    path('salaryslipx/', page7,name='page7'),
    path('weekoff/',views.weekoff),
    path('weekoffdisplayadmin/', views.weekoffdisplayadmin),
    path('weekoffemployee/', views.weekoffemployee),
    path('appliedleaves/', views.appliedleaves),
    path('editprofile/', views.editprofile),
    path('publicholidays/', views.publicholidays),
    path('publicholidaysadmin/', views.publicholidaysadmin),
    path('publicholidaysemployee/', views.publicholidaysemployee),
    path('generate_sundays/', views.generate_sundays),
    path('calendar/<int:employee_id>/', view_monthly_details, name='view_monthly_details'),
    path('editattendance/<int:employee_id>', views.editattendance, name='editattendance'),
    path('fetch_data/<int:year>/<int:month>/', fetch_data, name='fetch_data'),
    path('fetch_dat/<int:year>/<int:month>/', fetch_dat, name='fetch_dat'),
    path('calendar/<str:employee_id>/save_salary_slip/', save_salary_slip, name='save_salary_slip'),
    path('holidaycalendar/', holidaycalendar, name='holidaycalendar'),
    
    ]




    