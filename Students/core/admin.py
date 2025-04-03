from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.forms import SetPasswordForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import (
    Branch, Division, Mentor, Student,
    Subject, ElectiveGroup, StudentSubject,
    InternalAssessment, EndSemesterExam,
    Project, SemesterResult, CSVInput
)

# Custom Student admin with password change link
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'email_id', 'branch', 'division', 'user_status', 'password_change_link')
    search_fields = ('roll_number', 'name', 'email_id')
    list_filter = ('branch', 'division')
    actions = ['create_user_accounts']
    
    def user_status(self, obj):
        if obj.user:
            return format_html('<span style="color: green;">✓ User exists</span>')
        else:
            return format_html('<span style="color: red;">✗ No user</span>')
    
    user_status.short_description = "User Account"
    
    def password_change_link(self, obj):
        if obj.user:
            # Direct link to password change form
            change_password_url = reverse('admin:auth_user_password_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="button" style="background-color: #79aec8; padding: 5px 10px; '
                'border-radius: 4px; color: white; text-decoration: none;">Change Password</a>',
                change_password_url
            )
        else:
            create_user_url = reverse('admin:create_user_for_student', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background-color: #ffbd5a; padding: 5px 10px; '
                'border-radius: 4px; color: white; text-decoration: none;">Create User</a>',
                create_user_url
            )
    
    password_change_link.short_description = "Password Management"
    
    def create_user_accounts(self, request, queryset):
        """Create user accounts for selected students."""
        users_created = 0
        for student in queryset:
            if not student.user:
                # Create a user with the roll number as username
                username = student.roll_number
                # Generate a default password (consider a more secure approach)
                default_password = f"default_{username}"
                
                # Check if a user with this username already exists
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=student.email_id,
                        password=default_password
                    )
                    # Link the user to the student
                    student.user = user
                    student.save()
                    users_created += 1
        
        messages.success(request, f"Created {users_created} user accounts. Default password format: default_ROLLNUMBER")
    
    create_user_accounts.short_description = "Create user accounts for selected students"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<str:student_id>/create-user/',
                self.admin_site.admin_view(self.create_user_view),
                name='create_user_for_student',
            ),
        ]
        return custom_urls + urls
    
    def create_user_view(self, request, student_id):
        """View to create a user for a student."""
        student = self.get_object(request, student_id)
        if student.user:
            messages.error(request, "This student already has a user account.")
            return HttpResponseRedirect(reverse('admin:core_student_change', args=[student_id]))
        
        # Create a user with the roll number as username
        username = student.roll_number
        # Generate a default password (consider a more secure approach)
        default_password = f"default_{username}"
        
        # Check if a user with this username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f"A user with username '{username}' already exists.")
            return HttpResponseRedirect(reverse('admin:core_student_change', args=[student_id]))
            
        user = User.objects.create_user(
            username=username,
            email=student.email_id,
            password=default_password
        )
        # Link the user to the student
        student.user = user
        student.save()
        
        messages.success(
            request, 
            f"User created successfully. Username: {username}, Default password: {default_password}"
        )
        return HttpResponseRedirect(reverse('admin:auth_user_password_change', args=[user.id]))

# Custom Mentor admin with password change link
class MentorAdmin(admin.ModelAdmin):
    list_display = ('mentor_id', 'name', 'email', 'user_status', 'password_change_link')
    search_fields = ('mentor_id', 'name', 'email')
    actions = ['create_user_accounts']
    
    def user_status(self, obj):
        if obj.user:
            return format_html('<span style="color: green;">✓ User exists</span>')
        else:
            return format_html('<span style="color: red;">✗ No user</span>')
    
    user_status.short_description = "User Account"
    
    def password_change_link(self, obj):
        if obj.user:
            # Direct link to password change form
            change_password_url = reverse('admin:auth_user_password_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="button" style="background-color: #79aec8; padding: 5px 10px; '
                'border-radius: 4px; color: white; text-decoration: none;">Change Password</a>',
                change_password_url
            )
        else:
            create_user_url = reverse('admin:create_user_for_mentor', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background-color: #ffbd5a; padding: 5px 10px; '
                'border-radius: 4px; color: white; text-decoration: none;">Create User</a>',
                create_user_url
            )
    
    password_change_link.short_description = "Password Management"
    
    def create_user_accounts(self, request, queryset):
        """Create user accounts for selected mentors."""
        users_created = 0
        for mentor in queryset:
            if not mentor.user:
                # Create a user with the mentor ID as username
                username = mentor.mentor_id
                # Generate a default password (consider a more secure approach)
                default_password = f"default_{username}"
                
                # Check if a user with this username already exists
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=mentor.email,
                        password=default_password
                    )
                    # Link the user to the mentor
                    mentor.user = user
                    mentor.save()
                    users_created += 1
        
        messages.success(request, f"Created {users_created} user accounts. Default password format: default_MENTORID")
    
    create_user_accounts.short_description = "Create user accounts for selected mentors"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<str:mentor_id>/create-user/',
                self.admin_site.admin_view(self.create_user_view),
                name='create_user_for_mentor',
            ),
            path(
                '<str:mentor_id>/set-password/',
                self.admin_site.admin_view(self.set_password_view),
                name='set_password_for_mentor',
            ),
        ]
        return custom_urls + urls
    
    def create_user_view(self, request, mentor_id):
        """View to create a user for a mentor."""
        mentor = self.get_object(request, mentor_id)
        if mentor.user:
            messages.error(request, "This mentor already has a user account.")
            return HttpResponseRedirect(reverse('admin:core_mentor_change', args=[mentor_id]))
        
        # Create a user with the mentor ID as username
        username = mentor.mentor_id
        # Generate a default password (consider a more secure approach)
        default_password = f"default_{username}"
        
        # Check if a user with this username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f"A user with username '{username}' already exists.")
            return HttpResponseRedirect(reverse('admin:core_mentor_change', args=[mentor_id]))
            
        user = User.objects.create_user(
            username=username,
            email=mentor.email,
            password=default_password
        )
        # Link the user to the mentor
        mentor.user = user
        mentor.save()
        
        messages.success(
            request, 
            f"User created successfully. Username: {username}, Default password: {default_password}"
        )
        return HttpResponseRedirect(reverse('admin:auth_user_password_change', args=[user.id]))
    
    def set_password_view(self, request, mentor_id):
        """View to set a password for a mentor user."""
        mentor = self.get_object(request, mentor_id)
        
        if not mentor.user:
            messages.error(request, "This mentor does not have a user account yet.")
            return HttpResponseRedirect(reverse('admin:core_mentor_change', args=[mentor_id]))
        
        # Redirect to the Django built-in password change form
        return HttpResponseRedirect(reverse('admin:auth_user_password_change', args=[mentor.user.id]))

# Custom User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Keep the fieldsets but ensure password management is visible
    fieldsets = UserAdmin.fieldsets

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register your models here.
admin.site.register(Branch)
admin.site.register(Division)
admin.site.register(Mentor, MentorAdmin)  # Register with custom admin
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject)
admin.site.register(ElectiveGroup)
admin.site.register(StudentSubject)
admin.site.register(InternalAssessment)
admin.site.register(EndSemesterExam)
admin.site.register(Project)
admin.site.register(SemesterResult)
admin.site.register(CSVInput)  # Register CSVInput model
