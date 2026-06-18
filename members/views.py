from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
import json
from .models import MemberInfo, Attendance

# ------------------- Home Page -------------------
def home(request):
    return render(request, 'home.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MemberInfo

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        designation = request.POST.get('designation')
        department = request.POST.get('department')
        subjects = request.POST.get('subjects')
        degree = request.POST.get('degree')
        experience = request.POST.get('experience')
        certifications = request.FILES.get('certifications')  # Handle file upload

        if not username or not email or not password or not first_name or not last_name:
            messages.error(request, "All required fields must be filled.")
            return redirect('register')

        if MemberInfo.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user_count = MemberInfo.objects.count()
        user_type = 'admin' if user_count == 0 else 'teacher'

        user = MemberInfo.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            designation=designation,
            department=department,
            subjects=subjects,
            degree=degree,
            experience=experience,
            certifications=certifications,
            user_type=user_type
        )

        messages.success(request, f"Registration successful! You are registered as {user_type}. Please log in.")
        return redirect('login')

    return render(request, 'register.html')


# ------------------- User Login -------------------
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('admin_dashboard' if user.user_type == 'admin' else 'teacher_dashboard')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


# ------------------- User Logout -------------------
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# ------------------- Admin Dashboard -------------------
@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, "Access denied!")
        return redirect('login')
    return render(request, 'admin_dashboard.html')


# ------------------- Teacher Dashboard -------------------
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def teacher_dashboard(request):
    if getattr(request.user, 'user_type', None) != 'teacher':
        messages.error(request, "Access denied!")
        return redirect('login')

    return render(request, 'teacher_dashboard.html', {'user': request.user})



# ------------------- Contact Page & Email -------------------
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not name or not email or not subject or not message:
            messages.error(request, "All fields are required.")
            return redirect('contact')

        try:
            send_mail(
                f"SchedSmart Contact - {subject}",
                f"Name: {name}\nEmail: {email}\nMessage:\n{message}",
                settings.DEFAULT_FROM_EMAIL,  # Configure in settings.py
                ['support@schedsmart.com'],  # Replace with your admin email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            messages.error(request, "Failed to send message. Please try again.")

        return redirect('contact')

    return render(request, 'contact.html')


# ------------------- Profile Page -------------------
@login_required
def profile(request):
    phone_number = getattr(request.user, 'phone_number', "").strip()
    if phone_number and not phone_number.startswith("+91 "):
        phone_number = "+91 " + phone_number

    designation = getattr(request.user, 'designation', "Assistant Professor")
    department = getattr(request.user, 'department', "Computer Science")  # Fetch from user model if stored

    teacher_data = {
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone_number": phone_number,
        "designation": designation,
        "department": department,
    }

    return render(request, 'profile.html', {"teacher": teacher_data})


# ------------------- Attendance -------------------
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Attendance, MemberInfo
import json

@login_required
def attendance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            date = data.get("date")
            status = data.get("status")

            # Ensure the logged-in user is a teacher
            if request.user.user_type != "teacher":
                return JsonResponse({"error": "Only teachers can mark attendance!"}, status=403)

            # Create attendance only for the logged-in teacher
            attendance = Attendance.objects.create(date=date, status=status, teacher=request.user)

            return JsonResponse({
                "success": True,
                "message": "Attendance marked successfully!",
                "id": attendance.id,
                "teacher_id": request.user.id,
                "teacher_name": request.user.get_full_name()
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # Fetch attendance records only for the logged-in teacher
    records = Attendance.objects.filter(teacher=request.user)

    return render(request, "attendance.html", {"records": records})

#--------message-------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def message(request):
    return render(request, 'message.html')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import MemberInfo, Timetable, Substitute, Attendance, Report

# Check if user is admin
def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

# Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    teachers = MemberInfo.objects.filter(user_type='teacher')
    timetables = Timetable.objects.all()
    substitutes = Substitute.objects.all()
    reports = Report.objects.all()
    
    return render(request, 'admin_dashboard.html', {
        'teachers': teachers,
        'timetables': timetables,
        'substitutes': substitutes,
        'reports': reports
    })

# Manage Timetable
@login_required
@user_passes_test(is_admin)
def manage_timetable(request):
    if request.method == 'POST':
        teacher_id = request.POST['teacher']
        subject = request.POST['subject']
        classroom = request.POST['classroom']
        time_slot = request.POST['time_slot']
        
        teacher = get_object_or_404(MemberInfo, id=teacher_id)
        Timetable.objects.create(teacher=teacher, subject=subject, classroom=classroom, time_slot=time_slot)
        messages.success(request, "Timetable entry added successfully!")
        return redirect('admin_dashboard')
    
    teachers = MemberInfo.objects.filter(user_type='teacher')
    return render(request, 'manage_timetable.html', {'teachers': teachers})

# Delete Timetable Entry
@login_required
@user_passes_test(is_admin)
def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id)
    timetable.delete()
    messages.success(request, "Timetable entry deleted successfully!")
    return redirect('admin_dashboard')




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MemberInfo, Timetable

@login_required
def admin_dashboard(request):
    total_teachers = MemberInfo.objects.filter(user_type="teacher").count()
    total_periods = Timetable.objects.count()
    total_subjects = Timetable.objects.values_list("subject", flat=True).distinct().count()
    total_classes = Timetable.objects.values_list("classroom", flat=True).distinct().count()

    context = {
        "total_teachers": total_teachers,
        "total_periods": total_periods,
        "total_subjects": total_subjects,
        "total_classes": total_classes,
    }
    return render(request, "admin_dashboard.html", context)


