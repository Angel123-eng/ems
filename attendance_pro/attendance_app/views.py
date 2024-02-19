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

# Dashborad of employee
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
    
    return render(request, 'editprofile.html')



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





def page6(request):
    id1=request.session['id']
    a=regmodel.objects.get(employeeid=id1)
    img=str(a.image).split('/')[-1]
    return render(request,'salaryx.html',{'a':a})

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

def employeedetails(request):
    a = regmodel.objects.all()
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

    pair = zip(uid, nme, emid, dsg, eml, blg, phno, db, jnd, img, accno, bknm, brc, ifs, sl)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        action = request.POST.get('action')

        employee = get_object_or_404(regmodel, id=employee_id)

        if action == 'inactive':
            employee.status = 'Active' if employee.status == 'Inactive' else 'Inactive'
        elif action == 'resigned':
            employee.status = 'Resigned'
        else:
            # Handle invalid action, if needed
            pass

        # Save the updated status
        employee.save()

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

            if psw == cpsw:
                b = regmodel(name=nm, employeeid=eid, designation=ds, email=em, bloodgroup=bg,
                             phonenumber=phn, dateofbirth=dob, joiningdate=jnd, image=img, accountnumber=acno,
                             bankname=bnknm, branch=br, ifsccode=ifsc, salary=sal, password=psw)
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

def display_attendance(request):
    try:
        # Fetch all records from the AttendanceModel
        attendance_records = AttendanceModel.objects.all()

        # Pass the records to the template for rendering
        return render(request, 'attendance_template.html', {'attendance_records': attendance_records})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
 
 
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
from .models import WeekoffModel
from .forms import WeekoffForm

from .models import WeekoffModel, ExtraModel
# Weekoff selection page for admin
from .models import WeekoffModel, ExtraModel
from django.utils import timezone

from django.shortcuts import get_object_or_404

def weekoff(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('name_'):
                employee_id = key.split('_')[1]

                form_data = {
                    'name': request.POST.get(f'name_{employee_id}'),
                    'employeeid': request.POST.get(f'employeeid_{employee_id}'),
                    'weekoff1': request.POST.get(f'weekoff1_{employee_id}'),
                    'weekoff2': request.POST.get(f'weekoff2_{employee_id}'),
                }

                form = WeekoffForm(form_data)

                if form.is_valid():
                    weekoff_instance = form.save()

                    # Check if there is an existing leave entry for weekoff1 and update it to 'Weekoff'
                    existing_leave1 = ExtraModel.objects.filter(
                        name=weekoff_instance.name,
                        employeeid=weekoff_instance.employeeid,
                        date=weekoff_instance.weekoff1,
                        status='Leave'
                    ).first()

                    if existing_leave1:
                        existing_leave1.status = 'Weekoff'
                        existing_leave1.save()

                    # Check if there is an existing leave entry for weekoff2 and update it to 'Weekoff'
                    existing_leave2 = ExtraModel.objects.filter(
                        name=weekoff_instance.name,
                        employeeid=weekoff_instance.employeeid,
                        date=weekoff_instance.weekoff2,
                        status='Leave'
                    ).first()

                    if existing_leave2:
                        existing_leave2.status = 'Weekoff'
                        existing_leave2.save()

        return redirect(admindashboard)  # Replace 'admindashboard' with the actual URL name or path
    else:
        form = WeekoffForm()

    a = regmodel.objects.filter(status='Active')

    return render(request, 'weekoff.html', {'a': a, 'form': form})




# Weekoff display page for admin
def weekoffdisplayadmin(request):
    try:
        # Fetch all records from the AttendanceModel
        weekoff_data = WeekoffModel.objects.all()

        # Pass the records to the template for rendering
        return render(request, 'weekoffdisplayadmin.html', {'weekoff_data': weekoff_data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
# Weekoff display page for employee
def weekoffemployee(request):
    try:
        # Fetch the employee ID from the session
        id1 = request.session.get('id')

        # Check if the employee ID exists in the session
        if id1 is not None:
            weekoff = WeekoffModel.objects.filter(employeeid=id1)

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

def publicholidays(request):
    if request.method == 'POST':
        date_value = request.POST.get('date')
        status = request.POST.get('status')

        # Check if Sundays for the current year are already stored
        current_year = timezone.now().year
        existing_sundays_count = PublicholidaysModel.objects.filter(date__year=current_year, status='Sunday').count()

        if existing_sundays_count == 0:
            # Generate and save Sundays for the current year
            sundays = generate_sundays(current_year)

            for sunday in sundays:
                public_holiday = PublicholidaysModel(date=sunday, status='Sunday')
                public_holiday.save()

                # Loop through each employee and save Sunday information to ExtraModel
                employees = regmodel.objects.all()  # Replace YourEmployeeModel with your actual employee model
                for employee in employees:
                    sunday_data = ExtraModel(name=employee.name, employeeid=employee.employeeid, date=sunday, status='Sunday')
                    sunday_data.save()

        # Loop through each employee and save the data to both models
        employees = regmodel.objects.all()  # Replace YourEmployeeModel with your actual employee model
        for employee in employees:
            extra_data = ExtraModel(name=employee.name, employeeid=employee.employeeid, date=date_value, status='Holiday')
            extra_data.save()

            public_holiday = PublicholidaysModel(date=date_value, status=status)
            public_holiday.save()

        return redirect(admindashboard)  # Redirect to the same page after submission

    # If it's not a POST request, check if Sundays for the current year are already stored
    current_year = timezone.now().year
    existing_sundays_count = PublicholidaysModel.objects.filter(date__year=current_year, status='Sunday').count()

    if existing_sundays_count == 0:
        # If Sundays are not stored, generate and save them
        sundays = generate_sundays(current_year)

        for sunday in sundays:
            public_holiday = PublicholidaysModel(date=sunday, status='Sunday')
            public_holiday.save()

            # Loop through each employee and save Sunday information to ExtraModel
            employees = regmodel.objects.all()  # Replace YourEmployeeModel with your actual employee model
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

def view_monthly_details(request, employee_id):
    request.session['empid'] = employee_id
    employees = ExtraModel.objects.filter(employeeid=employee_id).values('name', 'employeeid').distinct()
    
    if employees.exists():
        # Fetch salary information from RegModel
        employee_salary = get_object_or_404(regmodel, employeeid=employee_id).salary

        return render(request, 'calendar.html', {'employees': employees, 'salary': employee_salary})
    else:
        return render(request, 'employee_not_found.html')





def fetch_dat(request, year, month):
    empid = request.session.get('empid', None)  # Retrieve empid from the session
    print("employee id =", empid)

    # Calculate start and end dates for the selected month
    start_date = date(year, month, 26)
    if month == 12:
        end_date = date(year + 1, 1, 25)
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

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


@csrf_exempt
@require_POST
def save_salary_slip(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        # Print received data for debugging
        print("Received data:", data)

      # Extract data from the JSON using correct keys
        name = data.get('name', '')
        employeeid = data.get('employeeid', '')
        month = data.get('month', '')
        year = data.get('year', 0)  # Assuming the year is an integer
        totalworkingdays = data.get('totalworkingdays', 0)
        salarydeductedleave = data.get('salarydeductedleave', 0)
        salary = data.get('salary', 0)
        deductionamount = data.get('deductionamount', 0)
        monthlysalary = data.get('monthlysalary', 0)


        # Create and save a new SalarySlipModel instance
        salary_slip = SalarySlipModel(
            name=name,
            employeeid=employeeid,
            month=month,
            year=year,
            totalworkingdays=totalworkingdays,
            salarydeductedleave=salarydeductedleave,
            salary=salary,
            deductionamount=deductionamount,
            monthlysalary=monthlysalary
        )
        salary_slip.save()

        return JsonResponse({'message': 'Data saved successfully'}, status=200)

    except Exception as e:
        print("Error:", e)
        return JsonResponse({'error': str(e)}, status=500)

def holidaycalendar(request):
    return render(request, 'holidaycalendar.html')

