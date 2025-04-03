from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import StudentLoginForm, MentorLoginForm, AdminLoginForm
from django.contrib import messages
from django.contrib.auth.models import User
from core.models import Student, Mentor

def home(request):
    """Home page with links to different login options"""
    return render(request, 'home.html')

def student_login(request):
    """Student login view"""
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if student record exists and is linked to the user
                student_linked = Student.objects.filter(user=user).exists()
                
                if student_linked:
                    # User is already linked to a student record
                    auth_login(request, user)
                    return redirect('core:home')
                else:
                    # Check if a student record exists with this roll number
                    student_record = Student.objects.filter(roll_number=username).first()
                    
                    if student_record:
                        # Student record exists but is not linked to the user
                        # Link the student record to this user
                        student_record.user = user
                        student_record.save()
                        messages.success(request, "Your account has been linked to your student record.")
                        auth_login(request, user)
                        return redirect('core:home')
                    else:
                        messages.error(request, "No student record found with your roll number. Please contact the administrator.")
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Invalid form submission")
    else:
        form = StudentLoginForm()
    
    return render(request, 'Login/student_login.html', {'form': form})

def mentor_login(request):
    """Mentor login view"""
    if request.method == 'POST':
        form = MentorLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if Mentor.objects.filter(user=user).exists():
                    auth_login(request, user)
                    return redirect('core:home')
                else:
                    messages.error(request, "User is not linked to a Mentor model")
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Invalid form submission")
    else:
        form = MentorLoginForm()
    
    return render(request, 'Login/mentor_login.html', {'form': form})

def admin_login(request):
    """Admin login view"""
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                auth_login(request, user)
                # Redirect to CSV upload page instead of Django admin
                return redirect('core:upload_csv')
            else:
                messages.error(request, "Invalid credentials or insufficient permissions")
        else:
            messages.error(request, "Invalid form submission")
    else:
        form = AdminLoginForm()
    
    return render(request, 'Login/admin_login.html', {'form': form})

@login_required
def logout_view(request):
    """Logout view"""
    if request.method == 'POST':
        auth_logout(request)
        return redirect('home')
    return render(request, 'Logout/logout.html')
