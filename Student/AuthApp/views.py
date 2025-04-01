from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import StudentLoginForm, MentorLoginForm
from django.contrib import messages

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
                # TODO: Add verification that user is a student
                auth_login(request, user)
                return redirect('core:home')
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
                # TODO: Add verification that user is a mentor
                auth_login(request, user)
                return redirect('core:home')
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
                # Redirect to admin dashboard or Django admin
                return redirect('admin:index')
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
    auth_logout(request)
    return redirect('home')
