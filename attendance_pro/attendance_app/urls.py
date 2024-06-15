from django.urls import path
from . import views 
from .views import *
from .views import handle_frontend_data
from django.urls import path
from .views import display_attendance


urlpatterns=[
    
    # Employee
    path('',views.signin),
    path('signin/',views.signin),
    path('logentry', handle_frontend_data, name='handle_frontend_data'),
    path('base/', base, name='base'),
    path('dashboard/', page2, name='page2'),
    path('profilex/',page3,name='page3'),
    path('editprofile/', views.editprofile),
    path('attendancex/',page4, name='page4'),
    path('fetch_data/<int:year>/<int:month>/', fetch_data, name='fetch_data'),
    path('holidaycalendar/', holidaycalendar, name='holidaycalendar'),
    path('leaveapplicationx/',page5, name='page5'),
    path('leavestatus/',views.leavestatus),
    path('weekoffemployee/', views.weekoffemployee),
    path('publicholidaysemployee/', views.publicholidaysemployee),
    path('salaryx/',page6, name='page6'),
    path('productivityemployee/',productivityemployee, name='productivityemployee'),
    path('signout/', signout, name='signout'),    

    # Admin
    path('adminlogin/',views.adminlogin),
    path('admindashboard/',views.admindashboard),
    path('employeedetails/',views.employeedetails),
    path('register/',views.register),
    path('resigned_employees/', views.resigned_employees, name='resigned_employees'),
    path('terminated_employees/', views.terminated_employees, name='terminated_employees'),
    path('calendar/<int:employee_id>/', view_monthly_details, name='view_monthly_details'),
    path('fetch_dat/<int:year>/<int:month>/', fetch_dat, name='fetch_dat'),
    path('editattendance/<int:employee_id>', views.editattendance, name='editattendance'),
    path('editemployeedetails/<int:id>',views.editemployeedetails),
    path('productivity/<int:employee_id>/', productivity, name='productivity'),    
    path('display_attendance/', display_attendance, name='display_attendance'),
    path('display_attendance_details/', display_attendance_details, name='display_attendance_details'),
    path('leavedisplay/',views.leavedisplay),
    path('leave/<int:id>',views.leave),
    path('appliedleaves/', views.appliedleaves),
    path('weekoff/',views.weekoff),
    path('weekoffdisplayadmin/', views.weekoffdisplayadmin),
    path('publicholidays/', views.publicholidays),
    path('publicholidaysadmin/', views.publicholidaysadmin),
    path('display_productivity_data/',display_productivity_data,name='display_productivity_data'),
    path('adminlogout/', adminlogout, name='adminlogout'),
    path('generate_sundays/', views.generate_sundays),
    path('calculate_working_hours/', calculate_working_hours, name='calculate_working_hours'),
    path('save_department/', views.save_department, name='save_department'),
    path('get_departments/', get_departments, name='get_departments'), 
    path('view-pdf/<path:file_path>/', view_pdf, name='view_pdf'),
    path('change-password/', change_password, name='change_password'),
    path('holiday/<str:date>/delete/', views.delete_holiday, name='delete_holiday'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('managerlogin/', views.managerlogin, name='managerlogin'),
    path('managerdashboard/',views.managerdashboard),
    path('managerlogout/', managerlogout, name='managerlogout'),
    path('editemployeedetailsmanager/<int:id>',views.editemployeedetailsmanager),
    path('resigned_employeesmanager/', views.resigned_employeesmanager, name='resigned_employeesmanager'),
    path('departments/', department_list, name='department_list'),
    path('editemployeedetails/<int:id>/', views.editemployeedetails, name='editemployeedetails'),
    path('save_reporting_manager/', views.save_reporting_manager, name='save_reporting_manager'),
    path('update_department/', update_department, name='update_department'),
    path('employeeman/', views.employeedetailsman),
    path('calendarman/<int:employee_id>/', views.calendarman),
    path('productivityman/<int:employee_id>/', views.productivityman), 
    path('leavemanager/',views.leavemanager),
    path('leaveman/<int:id>',views.leaveman),
    path('productivitymanager/',views.productivitymanager),
    path('save_assets/', views.save_assets, name='save_assets'),
    path('assets/', views.assets, name='assets'),
    path('update_asset', update_asset, name='update_asset'),
    path('delete_asset', delete_asset, name='delete_asset'),
    path('save-comments/', save_comments, name='save_comments'),
    path('comments/<int:employeeid>/', get_comments, name='get_comments'),
    path('delete/<int:entry_id>/', delete_entry, name='delete_entry'),  
      
    
    
    
    
    
    

   

    
    
]