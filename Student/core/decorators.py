from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import Student, Mentor
from functools import wraps

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # First ensure user is logged in
        if not request.user.is_authenticated:
            return redirect('student_login')
        
        # Check if user is linked to a Student model
        if Student.objects.filter(user=request.user).exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. You need a student account to view this page.")
            return redirect('home')
    return _wrapped_view

def mentor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # First ensure user is logged in
        if not request.user.is_authenticated:
            return redirect('mentor_login')
        
        # Check if user is linked to a Mentor model
        if Mentor.objects.filter(user=request.user).exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. You need a mentor account to view this page.")
            return redirect('home')
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. You need admin privileges to view this page.")
            return redirect('home')
    return _wrapped_view