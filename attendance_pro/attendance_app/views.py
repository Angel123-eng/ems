from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from .forms import *
from .models import *
import os
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from datetime import date

from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
from dateutil import parser
from django.db.models import Count
from .models import regmodel,AttendanceModel,LeaveModel
from .forms import logform,LeaveForm
# Create your views here.


# views.py


# For calculating the login, logoff time
@require_POST
def handle_frontend_data(request):
    try:
        # Get data from the request
        data = json.loads(request.body)
        userid = request.session.get('id')
        
        # Fetch the employee details based on the user ID
        employee = regmodel.objects.get(employeeid=userid)
        
        # Extract the name from the fetched employee details
        name = employee.name
    
        
        logintime_str = data.get('logintime')
        logintime = parser.parse(logintime_str)
        print("logintime fetched ===>  ", logintime)
        logofftime_str = data.get('logofftime')
        logofftime = parser.parse(logofftime_str)
        
        totalbreakTimex = data.get('totalbreakTimex')
        totalmeetingTimex = data.get('totalmeetingTimex')
        totaldownTimex = data.get('totaldownTimex')
        totalworkx = data.get('totalworkx')

        # Calculate working hours
        working_hours = (logofftime - logintime).total_seconds() / 3600  # Convert seconds to hours

        # Get the current date
        current_date = timezone.now().date()

        # Check if a record for this user and date already exists in AttendanceModel
        existing_attendance_record = AttendanceModel.objects.filter(employeeid=userid, created=current_date).first()

        if existing_attendance_record:
            # Update the existing AttendanceModel record
            existing_attendance_record.logintime = logintime
            existing_attendance_record.logofftime = logofftime
            existing_attendance_record.totalbreakTimex = totalbreakTimex
            existing_attendance_record.totalmeetingTimex = totalmeetingTimex
            existing_attendance_record.totaldownTimex = totaldownTimex
            existing_attendance_record.totalworkx = totalworkx
            existing_attendance_record.save()
        else:
            # Create a new AttendanceModel record
            AttendanceModel.objects.create(
                name=name,
                employeeid=userid,
                logintime=logintime,
                logofftime=logofftime,
                totalbreakTimex=totalbreakTimex,
                totalmeetingTimex=totalmeetingTimex,
                totaldownTimex=totaldownTimex,
                totalworkx=totalworkx,
                created=current_date
            )

        # Create or update ExtraModel record
        extra_model_record, created = ExtraModel.objects.get_or_create(
            employeeid=userid,
            date=current_date
        )

        # Determine the status based on working hours
        if working_hours >= 7:
            # Full day present
            extra_model_record.status = 'Present'
        elif 5 <= working_hours < 7:
            # Half day present
            extra_model_record.status = 'Half day'
        else:
            # Absent
            extra_model_record.status = 'Absent'

        extra_model_record.name = name
        extra_model_record.save()

        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



# Side and top navbar page of employee
def base(request):
    return render(request, 'base.html')

# Dashboard of employee
def page2(request):
    id1=request.session['id']
    a=regmodel.objects.get(employeeid=id1)
    img=str(a.image).split('/')[-1]
    return render(request,'dash.html',{'a':a})

# Profile page of employee
def page3(request):
    id1 = request.session['id']
    a = regmodel.objects.get(employeeid=id1)
    img = str(a.image).split('/')[-1]
    return render(request, 'profilex.html', {'a': a, 'img': img})



def editprofile(request):
    id1 = request.session['id']
    a = regmodel.objects.get(employeeid=id1)
    img = str(a.image).split('/')[-1]
    return render(request, 'editprofile.html', {'a':a, 'img':img})



# Monthly status display of employee
from django.shortcuts import render
from .models import regmodel, ExtraModel

def page4(request):
    id1 = request.session['id']
    a = regmodel.objects.get(employeeid=id1)
    attendance_records = ExtraModel.objects.filter(employeeid=id1).order_by('date')

    return render(request, 'attendancex.html', {'a': a, 'attendance_records': attendance_records})



from django.http import JsonResponse
from .models import ExtraModel

def fetch_data(request, year, month):
    id1 = request.session['id']
    records = ExtraModel.objects.filter(employeeid=id1, date__year=year, date__month=month).order_by('date').values()
    return JsonResponse(list(records), safe=False)


# Leave application of employee
from django.db.models import Q

from datetime import timedelta

def page5(request):
    id1 = request.session['id']
    employee = regmodel.objects.get(employeeid=id1)

    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave_instance = form.save(commit=False)
            leave_instance.applieddate = timezone.now()

            # Check if the 'half_day' radio button is selected
            if leave_instance.leaveType == 'Half Day':
                # Set the days to 0.5 for half-day leave
                leave_instance.days = 0.5
            else:
                # Retrieve 'from_date' and 'to_date' from the form
                from_date = form.cleaned_data['fromdate']
                to_date = form.cleaned_data['todate']

                # Check if both 'from_date' and 'to_date' are not None
                if from_date and to_date:
                    # Check if any public holidays fall within the specified range
                    public_holidays = PublicholidaysModel.objects.filter(date__range=[from_date, to_date])

                    # Check if any week-offs fall within the specified range
                    week_offs = WeekoffModel.objects.filter(
                        employeeid=id1,
                        weekoff1__range=[from_date, to_date],
                        weekoff2__range=[from_date, to_date]
                    )

                    # Create a set to store all excluded dates
                    excluded_dates = set()

                    # Exclude public holidays
                    for holiday in public_holidays:
                        excluded_dates.add(holiday.date)

                    # Exclude week-offs
                    for week_off in week_offs:
                        excluded_dates.add(week_off.weekoff1)
                        # Assuming weekoff2 is also a date field
                        excluded_dates.add(week_off.weekoff2)

                    # Calculate the difference in days, excluding public holidays and week-offs
                    days_difference = (to_date - from_date).days + 1

                    for date in excluded_dates:
                        if from_date <= date <= to_date:
                            days_difference -= 1

                    # Set the calculated days to the leave instance
                    leave_instance.days = days_difference

            # Associate the leave with the employee
            leave_instance.employee = employee

            # Save the leave instance to the database
            leave_instance.save()

            return redirect(page2)

    else:
        form = LeaveForm()

    return render(request, 'leaveapplicationx.html', {'a': employee, 'form': form})





# def page6(request):
#     id1=request.session['id']
#     a=regmodel.objects.get(employeeid=id1)
#     img=str(a.image).split('/')[-1]
#     return render(request,'salaryx.html',{'a':a})

from django.shortcuts import render
from .models import SalarySlipModel

def page6(request):
    if request.method == 'POST':
        # Get employee ID from session
        id1 = request.session.get('id')
        
        # Get selected month and year from the form data
        selected_month_year = request.POST.get('month-year-picker')
        selected_date = datetime.strptime(selected_month_year, '%Y-%m')
        
        # Filter the SalarySlipModel objects based on employee ID and selected month/year
        salary_slips = SalarySlipModel.objects.filter(employeeid=id1, month=selected_date.strftime('%B'), year=selected_date.year)
        
        # Fetch employee details
        employee = regmodel.objects.get(employeeid=id1)
        
        # Extract image filename
        #img = str(employee.image).split('/')[-1]
        #, 'selected_month_year': selected_month_year
        return render(request, 'salaryx.html', {'a': employee, 'salary_slips': salary_slips})
    else :
        return render(request, 'salaryx.html')  
    
     
        
def page7(request):
    id1=request.session['id']
    a=regmodel.objects.get(employeeid=id1)
    return render(request, 'salaryslipx.html',{'a':a})



#Admin login

def adminlogin(request):
    if request.method=='POST':
        a=adminloginform(request.POST)
        if a.is_valid():
            username=a.cleaned_data['username']
            password=a.cleaned_data['password']
            user=authenticate(request,username=username,password=password)
            if user is not None:
                return redirect(admindashboard)
            else:
                return HttpResponse("login failed")
    return render(request,'adminlogin.html')



from django.contrib.auth import logout

#Admin logout
def adminlogout(request):
    logout(request)
    return redirect(adminlogin)  # Replace 'adminlogin' with the actual URL name for your admin login page


# Admin dashboard
def admindashboard(request):
    return render(request,'admindashboard.html')


# Employee details display for admin
from django.shortcuts import render
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from .models import regmodel

from django.shortcuts import render, get_object_or_404, redirect
from .models import regmodel

def employeedetails(request):
    a = regmodel.objects.filter(status__in=['Active', 'Inactive'])
    uid = []
    nme = []
    emid = []
    dsg = []
    eml = []
    blg = []
    phno = []
    db = []
    jnd = []
    img = []
    accno = []
    bknm = []
    brc = []
    ifs = []
    sl = []
    lgt = []
    adr = []
    s = []
    

    for i in a:
        id = i.id
        uid.append(id)
        nm = i.name
        nme.append(nm)
        eid = i.employeeid
        emid.append(eid)
        ds = i.designation
        dsg.append(ds)
        em = i.email
        eml.append(em)
        bg = i.bloodgroup
        blg.append(bg)
        phn = i.phonenumber
        phno.append(phn)
        dob = i.dateofbirth
        db.append(dob)
        jn = i.joiningdate
        jnd.append(jn)
        im = str(i.image).split('/')[-1]
        img.append(im)
        acno = i.accountnumber
        accno.append(acno)
        bnknm = i.bankname
        bknm.append(bnknm)
        br = i.branch
        brc.append(br)
        ifsc = i.ifsccode
        ifs.append(ifsc)
        sal = i.salary
        sl.append(sal)
        lg = i.logintime
        lgt.append(lg)
        add = i.address
        adr.append(add)
        sts= i.status
        s.append(sts)
        

    pair = zip(uid, nme, emid, dsg, eml, blg, phno, db, jnd, img, accno, bknm, brc, ifs, sl, lgt, adr, s)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        action = request.POST.get('action')

        employee = get_object_or_404(regmodel, id=employee_id)

        if action == 'inactive':
            employee.status = 'Active' if employee.status == 'Inactive' else 'Inactive'
        elif action == 'active':
            employee.status = 'Inactive' if employee.status == 'Active' else 'Active'
        elif action == 'resigned':
            employee.status = 'Resigned'
        else:
            # Handle invalid action, if needed
            pass
        
        # Save the updated status
        employee.save()
        
        return redirect(employeedetails)  # Redirect to the same view after processing the form submission

    return render(request, 'employeedetails.html', {'a': pair})






# Assuming ExtraModel and ExtraForm are defined in your models.py and forms.py files

from django.shortcuts import render, redirect, get_object_or_404
from .models import ExtraModel
from .forms import ExtraForm

from django.shortcuts import render, get_object_or_404
from .models import ExtraModel
from .forms import ExtraForm

def editattendance(request, employee_id):
    # Get a list of ExtraModel instances matching the employee_id
    extra_instances = ExtraModel.objects.filter(id=employee_id)

    # Check if there are no matching records
    if not extra_instances.exists():
        return render(request, '404.html')  # Or handle appropriately for no matching records

    # If there are multiple records, choose one (you might want to define specific logic here)
    extra_instance = extra_instances.first()

    if request.method == 'POST':
        # Create a form instance with only the 'status' field
        form = ExtraStatusForm(request.POST, instance=extra_instance)

        if form.is_valid():
            # Update only the 'status' field and save the instance
            extra_instance.status = form.cleaned_data['status']
            extra_instance.save()

            return redirect(employeedetails)  # Adjust the URL name accordingly
    else:
        # Create a form instance with only the 'status' field
        form = ExtraStatusForm(initial={'status': extra_instance.status})

    return render(request, 'editattendance.html', {'employee_details': extra_instance, 'form': form})







# Employee details edit for admin
def editemployeedetails(request,id):
    a=regmodel.objects.get(id=id)
    img=str(a.image).split('/')[-1]
    if request.method=='POST':
        a.name=request.POST.get('name')
        a.employeeid=request.POST.get('employeeid')
        a.designation=request.POST.get('designation')
        a.email=request.POST.get('email')
        a.bloodgroup=request.POST.get('bloodgroup')
        a.phonenumber=request.POST.get('phonenumber')
        a.dateofbirth=request.POST.get('dateofbirth')
        a.joiningdate=request.POST.get('joiningdate')
        a.accountnumber=request.POST.get('accountnumber')
        a.bankname=request.POST.get('bankname')
        a.branch=request.POST.get('branch')
        a.ifsccode=request.POST.get('ifsccode')
        a.salary=request.POST.get('salary')
        a.logintime=request.POST.get('logintime')
        a.address=request.POST.get('address')
        if len(request.FILES) != 0:
            if len(a.image) != 0:
                os.remove(a.image.path)
            a.image = request.FILES['image']
        a.save()
        return redirect(employeedetails)
    return render(request,'editemployeedetails.html',{'a':a,'img':img})






from django.shortcuts import render
from django.http import HttpResponse

def monthlyattendance(request):
    active_employees = regmodel.objects.filter(status='Active')

    return render(request, 'monthlyattendance.html', {'a': active_employees})



# Employee registration for admin
def register(request):
    if request.method == 'POST':
        a = regform(request.POST, request.FILES)
        if a.is_valid():
            nm = a.cleaned_data['name']
            eid = a.cleaned_data['employeeid']
            ds = a.cleaned_data['designation']
            em = a.cleaned_data['email']
            bg = a.cleaned_data['bloodgroup']
            phn = a.cleaned_data['phonenumber']
            dob = a.cleaned_data['dateofbirth']
            jnd = a.cleaned_data['joiningdate']
            img = a.cleaned_data['image']
            acno = a.cleaned_data['accountnumber']
            bnknm = a.cleaned_data['bankname']
            br = a.cleaned_data['branch']
            ifsc = a.cleaned_data['ifsccode']
            sal = a.cleaned_data['salary']
            psw = a.cleaned_data['password']
            cpsw = a.cleaned_data['confirmpassword']
            lgt = a.cleaned_data['logintime']
            add = a.cleaned_data['address']

            if psw == cpsw:
                b = regmodel(name=nm, employeeid=eid, designation=ds, email=em, bloodgroup=bg,
                             phonenumber=phn, dateofbirth=dob, joiningdate=jnd, image=img, accountnumber=acno,
                             bankname=bnknm, branch=br, ifsccode=ifsc, salary=sal, password=psw, logintime=lgt, address=add)
                b.save()
                return redirect(employeedetails)
            else:
                return HttpResponse("Password doesn't match")
        else:
           
            return HttpResponse("Registration failed")
    return render(request, 'register.html')


# def attendance(request):
#     id1=request.session['id']
#     a=regmodel.objects.get(id=id1)
#     img=str(a.image).split('/')[-1]
#     return render(request,'attendance.html',{'a':a})



# def leaveapplication(request):
#     id1 = request.session['id']
#     employee = regmodel.objects.get(id=id1)

#     if request.method == 'POST':
#         form = LeaveForm(request.POST)
#         if form.is_valid():
#             leave_instance = form.save(commit=False)
#             leave_instance.employee = employee  # Assuming there's a ForeignKey in LeaveModel pointing to the employee
#             leave_instance.save()
#             return redirect(page2)  # Redirect to a success page after submission
#     else:
#         form = LeaveForm()

#     return render(request, 'leaveapplicationx.html', {'a': employee, 'form': form})


# def employeedashboard(request):
#     id1=request.session['id']
#     a=regmodel.objects.get(id=id1)
#     img=str(a.image).split('/')[-1]
#     return render(request,'dash.html',{'a':a})

# def profile(request):
#     id1=request.session['id']
#     a=regmodel.objects.get(id=id1)
#     img=str(a.image).split('/')[-1]
#     return render(request,'profilex.html',{'a':a,'img':img})


# def salary(request):
#     id1=request.session['id']
#     a=regmodel.objects.get(id=id1)
#     img=str(a.image).split('/')[-1]
#     return render(request,'salary.html',{'a':a})

# def salaryslip(request):
#     return render(request,'salaryslip.html')


# Employee signin
def signin(request):
    if request.method == 'POST':
        form = logform(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data['employeeid']
            print("Employee ID:", employee_id)  # Add this line to print the value of employee_id to the console

            password = form.cleaned_data['password']
            password = password.lower()

            employees = regmodel.objects.filter(employeeid=employee_id, password=password)

            if employees.exists():
                employee = employees.first()
                request.session['id'] = employee_id
                print("Session ID:", request.session['id'])

                return redirect(page2)  # Make sure you have a correct URL name

    return render(request, 'signin.html', {'form': logform()})


# Employee signout
def signout(request):
    # Check if the user is already logged in
    if 'id' in request.session:
        # If logged in, remove the user's session data
        del request.session['id']

    # Redirect to the desired logout success or home page
    return redirect('/signin/')  # Change 'home' to the desired URL or name for your home page




def tasks(request):
    id1=request.session['id']
    a=regmodel.objects.get(id=id1)
    img=str(a.image).split('/')[-1]
    return render(request,'tasks.html',{'a':a})


# Leave display for admin
def leavedisplay(request):
    a = LeaveModel.objects.filter(status='Pending')
    uid = []
    nm = []
    emp = []

    for i in a:
        id = i.id
        uid.append(id) 
        nme = i.name
        nm.append(nme)
        em = i.employeeid
        emp.append(em)

    pair = zip(uid, nm, emp)
    return render(request, 'leavedisplay.html', {'a': pair})


from .models import LeaveModel, ExtraModel
from datetime import timedelta

from datetime import timedelta

# views.py
from datetime import timedelta
from .models import LeaveModel, ExtraModel
from django.shortcuts import render


# Leave details display and status update for admin
from django.shortcuts import render, redirect
from datetime import timedelta
from .models import LeaveModel, ExtraModel

def leave(request, id):
    a = LeaveModel.objects.get(id=id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            a.status = 'Approved'
            
            # Update other fields if needed
            a.name = request.POST.get('name', a.name)
            a.employeeid = request.POST.get('employeeid', a.employeeid)
            a.fromdate = request.POST.get('fromdate', a.fromdate)
            a.todate = request.POST.get('todate', a.todate)
            a.reason = request.POST.get('reason', a.reason)
            a.days = request.POST.get('days', a.days)

            # Save the updated leave status and other fields
            a.save()

            # If the action is 'approve' and it is a half-day leave, create a new ExtraModel instance
            if a.days == 0.5:
                extra_instance = ExtraModel(
                    name=a.name,
                    employeeid=a.employeeid,
                    date=a.halfDayDate,
                    status='Half Day Leave'
                )
                extra_instance.save()
            else:
                # If it's a full-day leave, create a new ExtraModel instance for each date in the range
                from_date = a.fromdate
                to_date = a.todate

                while from_date <= to_date:
                    # Check if the leave date already exists in ExtraModel
                    existing_entry = ExtraModel.objects.filter(
                        employeeid=a.employeeid,
                        date=from_date
                    ).exists()

                    if not existing_entry:
                        # If the date doesn't exist, create a new ExtraModel instance
                        extra_instance = ExtraModel(
                            name=a.name,
                            employeeid=a.employeeid,
                            date=from_date,
                            status='Leave'
                        )
                        extra_instance.save()

                    # Move to the next date
                    from_date += timedelta(days=1)

            # Redirect to the admin dashboard after processing the leave request
            return redirect(admindashboard)  # Update 'admin_dashboard' with your actual URL name

        elif action == 'reject':
            a.status = 'Rejected'
            
            # Update other fields if needed
            a.name = request.POST.get('name', a.name)
            a.employeeid = request.POST.get('employeeid', a.employeeid)
            a.fromdate = request.POST.get('fromdate', a.fromdate)
            a.todate = request.POST.get('todate', a.todate)
            a.reason = request.POST.get('reason', a.reason)
            a.days = request.POST.get('days', a.days)

            # Save the updated leave status and other fields
            a.save()

            # Redirect to the admin dashboard after processing the leave request
            return redirect(admindashboard)  # Update 'admin_dashboard' with your actual URL name

    return render(request, 'leave.html', {'a': a})




# Employee attendance display for admin

# from datetime import datetime, time
# import pandas as pd
# from django.http import JsonResponse
# from django.shortcuts import render
# from .forms import ExcelUploadForm
# from .models import ExcelModel

# def display_attendance(request):
#     try:
#         # Process the Excel file upload form
#         if request.method == 'POST':
#             form = ExcelUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 # Get the uploaded file from the form
#                 excel_file = request.FILES['excel_file']

#                 # Read the Excel file using pandas
#                 df = pd.read_excel(excel_file)

#                 # Debug: Print the DataFrame to inspect the data
#                 print(df)

#                 # Create a list to store the inserted time data
#                 inserted_time_data = []

#                 # Iterate through rows and save to the database
#                 for index, row in df.iterrows():
#                     # Parse date from the Excel file format
#                     date_value = datetime.strptime(str(row['date']), "%Y-%m-%d").date()

#                     # Parse time from the Excel file format
#                     time_str = str(row['time'])
#                     if time_str.strip() == '00:00:00':
#                         # If the time is '00:00:00', provide a default time value
#                         time_value = time(0, 0)
#                     else:
#                         # Convert time string to time object directly
#                         time_parts = list(map(int, time_str.split(':')))
#                         time_value = time(*time_parts)

#                     # Create ExcelModel object and save to the database
#                     excel_instance = ExcelModel.objects.create(
#                         name=row['name'],
#                         employeeid=row['employeeid'],
#                         date=date_value,
#                         time=time_value
#                     )

#                     # Append the inserted time data to the list
#                     inserted_time_data.append({
#                         'name': excel_instance.name,
#                         'employeeid': excel_instance.employeeid,
#                         'date': excel_instance.date,
#                         'time': excel_instance.time,
#                     })

#                 # Return JsonResponse with inserted_time_data
#                 return JsonResponse({'status': 'success', 'message': 'Data uploaded successfully', 'inserted_time_data': inserted_time_data})

#             else:
#                 # Debug: Print form errors to identify validation issues
#                 print(form.errors)
#                 return JsonResponse({'status': 'error', 'message': form.errors.as_json()})

#         else:
#             form = ExcelUploadForm()

#         # Render the template with the form
#         return render(request, 'attendance_template.html', {'form': form})

#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)})


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ExcelUploadForm
from .models import ExcelModel
import pandas as pd

def display_attendance(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # Use pandas to read the Excel file
            df = pd.read_excel(excel_file)

            # Loop through the DataFrame and save each row to the database
            for index, row in df.iterrows():
                ExcelModel.objects.create(
                    employeeid=row['employeeid'],
                    name=row['name'],
                    date=row['date'],
                    intime=row['intime'],  # Adjust to the actual column name in your Excel file
                    outtime=row['outtime']  # Adjust to the actual column name in your Excel file
                )

            return HttpResponse('Data uploaded successfully!!!')
    else:
        form = ExcelUploadForm()

    return render(request, 'attendance_template.html', {'form': form})



from .models import ExcelModel

# def display_attendance_details(request):
#     # Retrieve all ExcelModel instances from the database
#     excel_data = ExcelModel.objects.all()

#     # Pass the data to the HTML page
#     return render(request, 'attendancedetails.html', {'excel_data': excel_data})

from datetime import datetime, date
from django.shortcuts import render
from .models import ExcelModel

from datetime import datetime, date
from django.shortcuts import render
from .models import ExcelModel

from django.shortcuts import render
from datetime import datetime, date, time
from .models import ExcelModel, ExtraModel

def calculate_working_hours(intime, outtime):
    if intime and outtime:
        delta = datetime.combine(date.today(), outtime) - datetime.combine(date.today(), intime)
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        working_hours = f"{hours} hours {minutes} minutes"
        return working_hours
    else:
        return "N/A"

def get_attendance_status(working_hours):
    if working_hours != "N/A":
        # Split the working_hours string into hours and minutes
        hours_str, minutes_str = working_hours.split(' hours ')
        
        # Convert hours and minutes to integers
        hours = int(hours_str)
        minutes = int(minutes_str.split(' minutes')[0])

        # Calculate total minutes
        total_minutes = hours * 60 + minutes

        if total_minutes >= 450:
            return "Present"
        elif 270 <= total_minutes < 450:
            return "Half Day Leave"
        else:
            return "Leave"
    else:
        return "N/A"
    


from .models import ExcelModel, ExtraModel

from django.shortcuts import get_object_or_404

from datetime import datetime, time

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def display_attendance_details(request):
    # Get all data ordered by date
    excel_data = ExcelModel.objects.all().order_by('-date')

    # Pagination
    paginator = Paginator(excel_data, 10)  # Show 10 records per page

    page = request.GET.get('page')
    try:
        excel_data = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        excel_data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        excel_data = paginator.page(paginator.num_pages)

    # Iterate over the paginated data and process as before
    for row in excel_data:
        row.working_hours = calculate_working_hours(row.intime, row.outtime)
        row.status = get_attendance_status(row.working_hours)
        existing_data = ExtraModel.objects.filter(employeeid=row.employeeid, date=row.date).first()
        reg_data = regmodel.objects.filter(employeeid=row.employeeid).values('name', 'logintime').first()
        if reg_data:
            intime_str = row.intime
            logintime_str = reg_data['logintime']
            logintime = datetime.strptime(logintime_str, '%H:%M').time()
            if row.status != "Leave" and intime_str > logintime:
                row.login = 'Latelogin'
            else:
                row.login = ''
            if existing_data:
                existing_data.name = reg_data['name'] if reg_data['name'] else row.name
                existing_data.status = row.status
                existing_data.login = row.login
                existing_data.save()
            else:
                extra_data = ExtraModel(name=reg_data['name'] if reg_data['name'] else row.name,
                                        employeeid=row.employeeid, date=row.date, status=row.status, login=row.login)
                extra_data.save()

    return render(request, 'attendancedetails.html', {'excel_data': excel_data})




# from .models import ExcelModel, ExtraModel

# from django.shortcuts import get_object_or_404

# from datetime import datetime, time

# from datetime import datetime

# def display_attendance_details(request):
#     excel_data = ExcelModel.objects.all()

#     for row in excel_data:
#         # Calculate working hours and get attendance status
#         row.working_hours = calculate_working_hours(row.intime, row.outtime)
#         row.status = get_attendance_status(row.working_hours)

#         # Check if data already exists for the employee on that date
#         existing_data = ExtraModel.objects.filter(employeeid=row.employeeid, date=row.date).first()

#         # Retrieve the registered name and logintime
#         registered_info = regmodel.objects.filter(employeeid=row.employeeid).values('name', 'logintime').first()

#         if registered_info:
#             logintime_str = registered_info['logintime']
#             logintime = datetime.strptime(logintime_str, '%H:%M').time()

#             # Extract hours and minutes from intime and logintime
#             intime_hours, intime_minutes = row.intime.hour, row.intime.minute
#             logintime_hours, logintime_minutes = logintime.hour, logintime.minute

#             # Compare hours and minutes
#             if (intime_hours > logintime_hours) or \
#                (intime_hours == logintime_hours and intime_minutes > logintime_minutes):
#                 row.status = 'Late Login'

#         if existing_data:
#             # Update existing record
#             existing_data.name = registered_info['name'] if registered_info else row.name
#             existing_data.status = row.status
#             existing_data.save()
#         else:
#             # Create a new record
#             extra_data = ExtraModel(name=registered_info['name'] if registered_info else row.name, 
#                                     employeeid=row.employeeid, date=row.date, status=row.status)
#             extra_data.save()

#     return render(request, 'attendancedetails.html', {'excel_data': excel_data})





 # Applied leaves display for admin   
def appliedleaves(request):
    try:
        # Fetch all records from the AttendanceModel
        appliedleaves = LeaveModel.objects.all()

        # Pass the records to the template for rendering
        return render(request, 'appliedleaves.html', {'appliedleaves': appliedleaves})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
# Leave status display for employee
from django.shortcuts import render
from django.http import JsonResponse
from .models import LeaveModel

def leavestatus(request):
    try:
        # Fetch the employee ID from the session
        id1 = request.session.get('id')

        # Check if the employee ID exists in the session
        if id1 is not None:
            # Fetch the leave status for the specific employee based on their ID
            leave_statuses = LeaveModel.objects.filter(employeeid=id1)

            # Pass the leave statuses to the template for rendering
            return render(request, 'leavestatus.html', {'leave_statuses': leave_statuses})
        else:
            # If the employee ID is not in the session, handle accordingly
            return JsonResponse({'status': 'error', 'message': 'Employee ID not found in session'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


from django.db.models import Sum
 
def attendancesalary(request, id):    
    start_date_str = request.GET.get('start', '')

    # Convert the start_date string to a datetime object
    start_date = datetime.strptime(start_date_str, "%Y-%m")

    print("start_date:", start_date)
    
    #start
    month = start_date.month
    year = start_date.year

    # Assuming id is the employee ID
    attendance_records = AttendanceModel.objects.filter(
        employeeid=id,
       logintime__month=month,
       logintime__year=year
    )

    for record in attendance_records:
        total_work_str = record.totalworkx
    
        # Split the string into parts
        parts = total_work_str.split()
    
        # Extract hours, minutes, and seconds from the parts
        total_work_hours = int(parts[0]) if parts[0] != '0' else 0
        total_work_minutes = int(parts[2]) if parts[2] != '0' else 0
        total_work_seconds = int(parts[4]) if parts[4] != '0' else 0
    
        total_work_duration = timedelta(
            hours=total_work_hours,
            minutes=total_work_minutes,
            seconds=total_work_seconds
        )

        if total_work_duration >= timedelta(hours=7, minutes=00, seconds=0):
            record.status = 'Present'
        elif total_work_duration >= timedelta(hours=5) and total_work_duration < timedelta(hours=7, minutes=00, seconds=0):
            record.status = 'Halfday'
        else:
            record.status = 'Absent'

            # Save the updated record
        record.save()
    #end
    month = start_date.month
    year = start_date.year
    count_present = AttendanceModel.objects.filter(
        employeeid=id,
        logintime__month=month,
        logintime__year=year,
        status='present'
    ).count()
    
    
    count_halfday = AttendanceModel.objects.filter(
        employeeid=id,
        logintime__month=month,
        logintime__year=year,
        status='halfday'
    ).count()
    
    count_absent = AttendanceModel.objects.filter(
        employeeid=id,
        logintime__month=month,
        logintime__year=year,
        status='absent'
    ).count()
    # count_ul = LeaveModel.objects.filter(
    #     employeeid=id,
    #     fromdate__month=month,
    #     todate__year=year
    # ).count()

    # count_hul = LeaveModel.objects.filter(
    #     employeeid=id,
    #     fromdate__month=month,
    #     todate__year=year
    # ).count()

   

    leave_count = LeaveModel.objects.filter(
    employeeid=id,
    status='Approved',
    fromdate__month=month,
    todate__year=year
).aggregate(Sum('days'))['days__sum']
    

    
    
    # count_hpl = LeaveModel.objects.filter(
    #     employeeid=id,
    #     fromdate__month=month,
    #     todate__year=year
    # ).count()

    # Calculate total leaves using the provided formula
    # tl = count_ul + (count_hul * 0.5) + count_pl + (count_hpl * 0.5)

#     # Print or use the total leaves value as needed
#     # print(f'Total Leaves (TL) for employee {id} in {month}/{year}: {tl}')

    # sdl = LeaveModel.objects.filter(
    #     employeeid=id,
    #     fromdate__month=month,
    #     todate__year=year
    # ).count()

    # sdl=count_ul + (count_hul * 0.5)

    count_h = PublicholidaysModel.objects.filter(
        date__month=month,
        date__year=year
    ).count()

#     ot = AttendanceModel.objects.filter(
#         employeeid=id,
#         status='O',
#         date__month=month,
#         date__year=year
#     ).count()

    count_wo = 2
    
    twd = count_present + count_h + count_wo 
#     count_s = AttendanceModel.objects.filter(
#         employeeid=id,
#         status='S',
#         date__month=month,
#         date__year=year
#     ).count()

#     th = count_h + count_wo + count_s

    user = regmodel.objects.get(employeeid=id)
    salary = user.salary

    # Calculate the per day salary
    pd = salary / 30

    # da = pd * sdl


#     count_nwd = AttendanceModel.objects.filter(
#         employeeid=id,
#         status='NWD',
#         date__month=month,
#         date__year=year
#     ).count()

#     poa = (pd * (30 - count_nwd) - da)


    #count = Attendance.objects.filter(employeeid=id, status='Present', date=start_date).count()
    a = AttendanceModel.objects.filter(employeeid=id)
    b = LeaveModel.objects.filter(employeeid=id)
    c = WeekoffModel.objects.filter(employeeid=id)
    user = regmodel.objects.get(employeeid=id)
    # print(count)
    if a.exists():
        return render(request,'attendancesalary.html', {'a': a,'b':b,'c':c, 'user':user,'count':count_present,'count_halfday':count_halfday,'count_absent':count_absent, 'pd':pd, 'leave_count':leave_count,'wo':count_wo, 'h':count_h, 'twd':twd})
        #return render(request, 'attendancesalary.html', {'a': a,'user':user,'count':count_present,'ul':count_ul, 'hul':count_hul, 'pl':count_pl, 'hpl':count_hpl, 'tl':tl, 'sdl':sdl, 'h':count_h, 'ot':ot, 'wo':count_wo, 's':count_s, 'th':th, 'pd':pd, 'da':da, 'nwd':count_nwd,'poa':poa})
    else:
        print(f"No Attendance records found for employee ID {id}")
        active_employees = regmodel.objects.filter(status='Active')

        return render(request, 'monthlyattendance.html', {'a': active_employees})
    


from django.shortcuts import render, redirect
from .models import WeekoffModel, ExtraModel
from .forms import WeekoffForm
from django.utils import timezone
from django.shortcuts import get_object_or_404

from django.shortcuts import render, redirect
from .models import ExtraModel
from .forms import ExtraForm  # Import your ExtraForm from forms.py

from django.shortcuts import render, redirect
from .models import regmodel, ExtraModel
from .forms import ExtraForm  # Import your ExtraForm from forms.py

from django.shortcuts import render, redirect
from .models import regmodel, ExtraModel
from .forms import ExtraForm

def weekoff(request):
    if request.method == 'POST':
        date = request.POST.get('date')  # Get the selected date

        # Get the list of selected employee IDs from the checkboxes
        selected_employee_ids = request.POST.getlist('employee_checkbox')

        for employee_id in selected_employee_ids:
            form_data = {
                'name': request.POST.get(f'name_{employee_id}'),
                'employeeid': request.POST.get(f'employeeid_{employee_id}'),
                'date': date,  # Use the selected date
                'status': 'Weekoff',
            }

            form = ExtraForm(form_data)

            if form.is_valid():
                form.save()

        return redirect(weekoff)  

    else:
        form = ExtraForm()
        a = regmodel.objects.filter(status='Active')

        return render(request, 'weekoff.html', {'a': a, 'form': form})










from django.shortcuts import render
from .models import ExtraModel

def weekoffdisplayadmin(request):
    try:
        # Fetch all unique dates from the ExtraModel where status is 'Weekoff'
        unique_dates = ExtraModel.objects.filter(status='Weekoff').values_list('date', flat=True).distinct()

        # Create a list to store the data for each date
        weekoff_data_by_date = []

        # Iterate over unique dates
        for date in unique_dates:
            # Fetch records for the current date and status 'Weekoff'
            records_for_date = ExtraModel.objects.filter(date=date, status='Weekoff')

            # Extract the name and employeeid for each record and store in a list
            records_data = [{'name': record.name, 'employeeid': record.employeeid} for record in records_for_date]

            # Append the data for the current date to the list
            weekoff_data_by_date.append({'date': date, 'records': records_data})

        # Pass the data to the template for rendering
        return render(request, 'weekoffdisplayadmin.html', {'weekoff_data_by_date': weekoff_data_by_date})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


    
# Weekoff display page for employee
def weekoffemployee(request):
    try:
        # Fetch the employee ID from the session
        id1 = request.session.get('id')

        # Check if the employee ID exists in the session
        if id1 is not None:
            weekoff = ExtraModel.objects.filter(employeeid=id1, status='Weekoff')

            return render(request, 'weekoffemployee.html', {'weekoff': weekoff})
        else:
            # If the employee ID is not in the session, handle accordingly
            return JsonResponse({'status': 'error', 'message': 'Employee ID not found in session'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
 
    
# Storing of sunday and public holiday into database by admin
from django.shortcuts import render, redirect
from .models import PublicholidaysModel , ExtraModel
from django.utils import timezone
from datetime import timedelta, date

def generate_sundays(year):
    # Get the first day of the year
    first_day = date(year, 1, 1)

    # Calculate the number of days to Sunday
    days_to_sunday = 6 - first_day.weekday()

    # Calculate the first Sunday of the year
    first_sunday = first_day + timedelta(days=days_to_sunday)

    # Generate all Sundays of the year
    sundays = [first_sunday + timedelta(weeks=i) for i in range((date(year, 12, 31) - first_sunday).days // 7 + 1)]

    return sundays

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import PublicholidaysModel, ExtraModel, regmodel

def publicholidays(request):
    if request.method == 'POST':
        date_value = request.POST.get('date')
        status = request.POST.get('status')

        # Check if Sundays for the current year are already stored
        current_year = timezone.now().year
        existing_sundays_count = ExtraModel.objects.filter(date__year=current_year, status='Sunday').count()

        if existing_sundays_count == 0:
            # Generate and save Sundays for the current year
            sundays = generate_sundays(current_year)

            for sunday in sundays:
                # Save Sundays to ExtraModel
                employees = regmodel.objects.all()  
                for employee in employees:
                    sunday_data = ExtraModel(name=employee.name, employeeid=employee.employeeid, date=sunday, status='Sunday')
                    sunday_data.save()

        # Loop through each employee and save the data to both models
        employees = regmodel.objects.all() 
        for employee in employees:
            # Save public holidays to ExtraModel
            extra_data = ExtraModel(name=employee.name, employeeid=employee.employeeid, date=date_value, status='Holiday')
            extra_data.save()

            # Save public holidays to PublicholidaysModel
            public_holiday = PublicholidaysModel(date=date_value, status=status)
            public_holiday.save()

        return redirect(admindashboard)  # Redirect to the same page after submission

    # If it's not a POST request, check if Sundays for the current year are already stored
    current_year = timezone.now().year
    existing_sundays_count = ExtraModel.objects.filter(date__year=current_year, status='Sunday').count()

    if existing_sundays_count == 0:
        # If Sundays are not stored, generate and save them
        sundays = generate_sundays(current_year)

        for sunday in sundays:
            # Save Sundays to ExtraModel
            employees = regmodel.objects.all()  
            for employee in employees:
                sunday_data = ExtraModel(name=employee.name, employeeid=employee.employeeid, date=sunday, status='Sunday')
                sunday_data.save()

    return render(request, 'publicholidays.html')




# Public holidays display for admin
from django.shortcuts import render
from django.http import JsonResponse
from .models import PublicholidaysModel

from django.db.models import Count

def publicholidaysadmin(request):
    try:
        # Fetch all records from the PublicholidaysModel where day is not 'Sunday'
        # Group the records by date and count the occurrences of each date
        publicholidays = (
            PublicholidaysModel.objects.exclude(status='Sunday')
            .values('date','status')
            .annotate(date_count=Count('date'))
        )

        # Pass the grouped records to the template for rendering
        return render(request, 'publicholidaysadmin.html', {'publicholidays': publicholidays})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



# Public holidays display for employee    
def publicholidaysemployee(request):
    try:
        # Fetch all records from the AttendanceModel
        a =  (PublicholidaysModel.objects.exclude(status='Sunday')
               .values('date','status')
            .annotate(date_count=Count('date'))
            )

        # Pass the records to the template for rendering
        return render(request, 'publicholidaysemployee.html', {'a': a})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



# Calendar display for admin
# from django.http import JsonResponse
# from django.shortcuts import render, get_object_or_404
# from .models import ExtraModel
# from datetime import datetime
# from calendar import monthcalendar

# def calendar(request, employeeid=None, year=None, month=None):
#     if year is None or month is None:
#         today = datetime.today()
#         year, month = today.year, today.month

#     month_calendar = monthcalendar(year, month)

#     context = {
#         'year': year,
#         'month': month,
#         'month_calendar': month_calendar,
#     }

#     if employeeid:
#         # Use get_object_or_404 to handle DoesNotExist
#         employee = get_object_or_404(regmodel, employeeid=employeeid)
#         extra_data = ExtraModel.objects.filter(employeeid=employeeid, date__year=year, date__month=month).order_by('date').values()
#         context.update({'employee': employee, 'extra_data': extra_data})

#     return render(request, 'calendar.html', context)

# def fetch_data(request, employeeid, year, month):
#     # Implement your logic to fetch data based on employeeid, year, and month
#     extra_data = ExtraModel.objects.filter(employeeid=employeeid, date__year=year, date__month=month).values()

#     return JsonResponse(list(extra_data), safe=False)


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ExtraModel, regmodel

# def view_monthly_details(request, employee_id):
#     request.session['empid'] = employee_id
#     employees = ExtraModel.objects.filter(employeeid=employee_id).values('name', 'employeeid').distinct()
    
#     if employees.exists():
#         # Fetch salary information from RegModel
#         employee_salary = get_object_or_404(regmodel, employeeid=employee_id).salary

#         return render(request, 'calendar.html', {'employees': employees, 'salary': employee_salary})
#     else:
#         return HttpResponse("Details does not exist!!!")

# from decimal import Decimal
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from .models import ExtraModel, regmodel, SalarySlipModel

# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from .models import ExtraModel, SalarySlipModel
# from decimal import Decimal

from decimal import Decimal
from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import ExtraModel, regmodel, SalarySlipModel

from decimal import Decimal, InvalidOperation

from django.http import JsonResponse


def view_monthly_details(request, employee_id):
    request.session['empid'] = employee_id
    employees = ExtraModel.objects.filter(employeeid=employee_id).values('name', 'employeeid').distinct()

    if employees.exists():
        employee_salary = get_object_or_404(regmodel, employeeid=employee_id).salary

        if request.method == 'POST':
            name = request.POST.get('name', '')
            month = request.POST.get('month', '')
            year = request.POST.get('year', '')

            total_working_days = convert_to_decimal(request.POST.get('totalPayableDays', 0))
            total_leave = convert_to_decimal(request.POST.get('totalleave', 0))
            paid_leave = convert_to_decimal(request.POST.get('paidleave', 0))
            late_login = convert_to_decimal(request.POST.get('Latelogin', 0))
            salary_deducted_leave = convert_to_decimal(request.POST.get('salarydeductedleave', 0))
            salary = convert_to_decimal(request.POST.get('salary', 0))
            per_day_salary = convert_to_decimal(request.POST.get('perdaysalary', 0))
            deduction_amount = convert_to_decimal(request.POST.get('deductionamount', 0))
            monthly_salary = convert_to_decimal(request.POST.get('monthlysalary', 0))

            # Check if incentive is provided
            incentive = Decimal(0)
            if 'incentive' in request.POST:
                incentive = convert_to_decimal(request.POST.get('incentive', 0))

            # Check if data already exists for the given employee and month
            existing_entry = SalarySlipModel.objects.filter(
                employeeid=employee_id,
                month=month,
                year=year
            ).first()

            if existing_entry:
                # Update existing entry
                existing_entry.name = name
                existing_entry.totalPayableDays = total_working_days
                existing_entry.totalleave = total_leave
                existing_entry.paidleave = paid_leave
                existing_entry.Latelogin = late_login
                existing_entry.salarydeductedleave = salary_deducted_leave
                existing_entry.salary = salary
                existing_entry.perdaysalary = per_day_salary
                existing_entry.deductionamount = deduction_amount
                existing_entry.incentive = incentive
                existing_entry.monthlysalary = monthly_salary
                existing_entry.save()
            else:
                # Insert new entry
                salary_slip = SalarySlipModel(
                    name=name,
                    employeeid=employee_id,
                    month=month,
                    year=year,
                    totalPayableDays=total_working_days,
                    totalleave=total_leave,
                    paidleave=paid_leave,
                    Latelogin=late_login,
                    salarydeductedleave=salary_deducted_leave,
                    salary=salary,
                    perdaysalary=per_day_salary,
                    deductionamount=deduction_amount,
                    incentive=incentive,
                    monthlysalary=monthly_salary
                )
                salary_slip.save()

            return JsonResponse({'message': "Salary Slip generated and saved successfully!"})

        return render(request, 'calendar.html', {'employees': employees, 'salary': employee_salary})
    else:
        return HttpResponse("Details do not exist!!!")


def convert_to_int(value):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def convert_to_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return Decimal(0)



def fetch_dat(request, year, month):
    empid = request.session.get('empid', None)  # Retrieve empid from the session
    print("employee id =", empid)

    # Calculate start and end dates for the selected month
    start_date = date(year, month, 26)
    if month == 12:
        end_date = date(year , month , 25)
    else:
        end_date = date(year, month, 25)

    # Calculate start date of the previous month
    if month == 1:
        prev_month_start = date(year - 1, 12, 26)
    else:
        prev_month_start = date(year, month - 1, 26)

    # Fetch data for the selected month
    records_current_month = ExtraModel.objects.filter(employeeid=empid, date__range=(prev_month_start, end_date)).order_by('date').values()

    # Fetch data for the specified year and month
    records_specified_month = ExtraModel.objects.filter(employeeid=empid, date__year=year, date__month=month).order_by('date').values()
    
   # records = ExtraModel.objects.filter(employeeid=empid, date__year=year, date__month=month).order_by('date').values()
    # Combine the results
    records_current_month_list = list(records_current_month)
    records_specified_month_list = list(records_specified_month)

    # Create a dictionary to hold both lists
    response_data = {
        'records_current_month': records_current_month_list,
        'records_specified_month': records_specified_month_list,
    }

    return JsonResponse(response_data, safe=False)

from django.shortcuts import render
from django.http import HttpResponse

def attendance_salary_view(request, employeeId):
    # Your logic to calculate attendance salary based on the employeeId
    # ...

    # For demonstration purposes, let's just return a simple response
    return HttpResponse(f"Attendance Salary for Employee ID {employeeId}")

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from .models import SalarySlipModel
from django.db import transaction
from decimal import Decimal

from decimal import Decimal




# class SaveSalarySlipView(View):

#     def post(self, request, employee_id, *args, **kwargs):
#         # Use cleaned data directly from the form
#         form_data = request.POST

#         # Validate if the employee_id in the form matches the one in the URL
#         if form_data.get('employeeid') != employee_id:
#             return HttpResponseBadRequest("Invalid employee_id")

#         # Function to safely convert a value to int or return 0 if the value is empty or invalid
#         def safe_int(value):
#             try:
#                 return int(value)
#             except (ValueError, TypeError):
#                 return 0

#         # Function to safely convert a value to Decimal or return 0 if the value is empty or invalid
#         def safe_decimal(value):
#             try:
#                 return Decimal(value)
#             except (ValueError, TypeError):
#                 return Decimal(0)

#         # Save data to the model with employee_id
#         with transaction.atomic():
#             salary_slip = SalarySlipModel.objects.create(
#                 name=form_data.get('name'),
#                 employeeid=form_data.get('employeeid'),
#                 month=form_data.get('month'),
#                 year=form_data.get('year'),
#                 totalworkingdays=safe_int(form_data.get('totalworkingdays')),
#                 totalleave=safe_int(form_data.get('totalleave')),
#                 salarydeductedleave=safe_int(form_data.get('salarydeductedleave')),
#                 salary=safe_decimal(form_data.get('salary')),
#                 deductionamount=safe_decimal(form_data.get('deductionamount')),
#                 monthlysalary=safe_decimal(form_data.get('monthlysalary'))
#             )

#         return render(request, 'calendar.html', {'salary_slip': salary_slip})





def holidaycalendar(request):
    return render(request, 'holidaycalendar.html')

# def fetch_extra_model_data(request, year, month):
#     # Add your logic to retrieve ExtraModel data (replace with your actual model and field names)
#     extra_model_data = ExtraModel.objects.filter(year=year, month=month).values('day', 'status')

#     # Convert extra_model_data to a list of dictionaries
#     extra_model_data_list = list(extra_model_data)

#     return JsonResponse(extra_model_data_list, safe=False)


from django.shortcuts import render
from .models import regmodel

def resigned_employees(request):
    resigned_employees = regmodel.objects.filter(status='Resigned')
    return render(request, 'resigned.html', {'resigned_employees': resigned_employees})



# from datetime import datetime, time, timedelta
# from .models import regmodel, ExcelModel

# # Define late login threshold (e.g., 15 minutes)
# late_threshold = timedelta(minutes=1) 

# # Fetch all records from both models
# regmodel_objects = regmodel.objects.all()
# excelmodel_objects = ExcelModel.objects.all()

# # Loop through ExcelModel objects and check for corresponding regmodel's logintime
# for excel_record in excelmodel_objects:
#     try:
#         reg_record = regmodel_objects.get(employeeid=excel_record.employeeid)
#         reg_logintime = datetime.strptime(reg_record.logintime, '%H:%M')
#         excel_intime = datetime.combine(datetime.today(), excel_record.intime)
#         late_time = reg_logintime + late_threshold

#         if excel_intime <= late_time:
#             excel_record.status = "Present"
#         else:
#             excel_record.status = "Late Login"
        
#         excel_record.save()
#     except regmodel.DoesNotExist:
#         # Handle the case where there's no corresponding record in regmodel
#         pass
    




from django.shortcuts import render, redirect
from .models import ProductivityModel

def productivity(request, employee_id):
    if request.method == 'POST':
        print(request.POST) 
        # Get data from the form
        name = request.POST.get('name')
        employeeid = request.POST.get('employeeid')
        month = request.POST.get('month')
        productivity = request.POST.get('productivity')
        quality = request.POST.get('quality')
        appreciations = request.POST.get('appreciations')
        extra_initiatives = request.POST.get('extraInitiatives')
        target = request.POST.get('target')
        achievement = request.POST.get('achievement')
        percentage = request.POST.get('percentage')
        new_client = request.POST.get('newClient')
        renewals = request.POST.get('renewals')

        # Create and save ProductivityModel instance
        productivity_instance = ProductivityModel(
            name=name,
            employeeid=employeeid,
            month=month,
            productivity=productivity,
            quality=quality,
            appreciations=appreciations,
            extraInitiatives=extra_initiatives,
            target=target,
            achievement=achievement,
            percentage=percentage,
            newClient=new_client,
            renewals=renewals
        )
        productivity_instance.save()

        # Redirect after successful submission
        return redirect(admindashboard)

    # Render the form template for GET requests
    return render(request, 'productivity.html', {'employee_id': employee_id})



from django.http import JsonResponse

def productivityemployee(request):
    try:
        # Fetch the employee ID from the session
        id1 = request.session.get('id')

        # Check if the employee ID exists in the session
        if id1 is not None:
            # Fetch the productivity data for the specific employee based on their ID
            productivity_data = ProductivityModel.objects.filter(employeeid=id1)

            # Pass the productivity data to the template for rendering
            return render(request, 'productivityemployee.html', {'productivity_data': productivity_data})
        else:
            # If the employee ID is not in the session, handle accordingly
            return JsonResponse({'status': 'error', 'message': 'Employee ID not found in session'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



from django.shortcuts import render
from .models import ProductivityModel

from django.shortcuts import render
from .models import ProductivityModel
from .models import regmodel

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import ProductivityModel

def display_productivity_data(request):
    # Retrieve all instances of ProductivityModel and reverse the queryset
    productivity_data = ProductivityModel.objects.all().order_by('-id')
    
    # Fetching names based on employee IDs
    employee_names = [(entry.employeeid, entry.name) for entry in regmodel.objects.all()]
    
    # Pagination
    paginator = Paginator(productivity_data, 10)  # 10 entries per page
    page = request.GET.get('page')
    try:
        productivity_data = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        productivity_data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        productivity_data = paginator.page(paginator.num_pages)
    
    # Pass the data and names to the template for rendering
    return render(request, 'productivityadmin.html', {'productivity_data': productivity_data, 'employee_names': employee_names})












