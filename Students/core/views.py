from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.urls import reverse
from .decorators import student_required, mentor_required, admin_required
from .forms import upload_CSVForm, Upload_CSVForm_Mentors, StudentRegistrationForm
from .models import Student, Mentor, CSVInput, Branch, Division, CSVInput_Mentors
from django.contrib.auth.models import User
import pandas as pd
import os
import io
from django.core.exceptions import ValidationError
from .validators import validate_roll_no
from django.db import connection

# Create your views here.
@login_required
def home(request):
    return render(request, 'core/home.html', {
        'user': request.user
    })

@student_required
def student_dashboard(request):
    # Get student data
    student = Student.objects.select_related('mentor_id').get(user=request.user)
    
    # Debug info
    print(f"Student: {student.roll_number}, Name: {student.name}")
    print(f"Mentor ID: {student.mentor_id_id}")  # This is how Django named the column
    
    # Try to fetch the mentor properly
    mentor_info = None
    if student.mentor_id_id:  # Check the database field directly
        try:
            # Get the mentor directly from the database
            mentor = Mentor.objects.get(mentor_id=student.mentor_id_id)
            mentor_info = {
                'id': mentor.mentor_id,
                'name': mentor.name,
                'email': mentor.email
            }
            print(f"Found mentor: {mentor.name} (ID: {mentor.mentor_id})")
        except Exception as e:
            print(f"Error fetching mentor: {str(e)}")
    else:
        print("No mentor assigned to this student")
    
    context = {
        'student': student,
        'user': request.user,
        'mentor_info': mentor_info
    }
    return render(request, 'core/student_dashboard.html', context)

@mentor_required
def mentor_dashboard(request):
    # Get mentor data and assigned students
    mentor = Mentor.objects.get(user=request.user)
    
    # Print mentor info for debugging
    print(f"Mentor ID: {mentor.mentor_id}, Name: {mentor.name}")
    
    # Use reverse relationship to retrieve assigned students
    students = mentor.students.all()
    print(f"Found {students.count()} students for mentor {mentor.name}")
    
    context = {
        'mentor': mentor,
        'students': students,
        'user': request.user
    }
    return render(request, 'core/mentor_dashboard.html', context)

@login_required
def admin_set_mentor_password(request, mentor_id):
    # Check if user is admin/staff
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')
    
    try:
        mentor = Mentor.objects.get(mentor_id=mentor_id)
        if not mentor.user:
            messages.error(request, "This mentor does not have a user account.")
            return redirect('admin:core_mentor_change', mentor_id)
        
        if request.method == 'POST':
            form = SetPasswordForm(mentor.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Password for {mentor.name} has been changed successfully.")
                return redirect('admin:core_mentor_change', mentor_id)
        else:
            form = SetPasswordForm(mentor.user)
        
        return render(request, 'core/admin_set_password.html', {
            'form': form,
            'mentor': mentor
        })
    except Mentor.DoesNotExist:
        messages.error(request, "Mentor not found.")
        return redirect('admin:core_mentor_changelist')

@admin_required
def upload_csv(request):
    # Check if a file already exists - limit to one upload at a time
    existing_files = CSVInput.objects.all()
    if existing_files.exists() and request.method == 'POST':
        messages.warning(request, "You already have an uploaded file. Please delete it before uploading a new one.")
        form = upload_CSVForm()
    elif request.method == 'POST':
        form = upload_CSVForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the uploaded file
                csv_file = form.cleaned_data['csv_file']
                
                # Read the file content
                file_content = csv_file.read().decode('utf-8')
                
                # Save the CSV content to the database
                csv_input = CSVInput.objects.create(
                    file_name=csv_file.name,
                    csv_content=file_content
                )
                
                # Confirm file upload success
                messages.success(request, f"File '{csv_file.name}' uploaded successfully!")
                
                try:
                    # Filter out comments (lines starting with //)
                    filtered_content = "\n".join(line for line in file_content.splitlines() if not line.startswith("//"))
                    filtered_file = io.StringIO(filtered_content)
                    df = pd.read_csv(filtered_file)
                    
                    # Display the first few rows for debugging
                    messages.success(request, f"CSV contains {len(df)} rows with columns: {', '.join(df.columns)}")
                    
                    # Keep track of stats for feedback
                    created_count = 0
                    updated_count = 0
                    linked_count = 0
                    student_created_count = 0
                    error_count = 0
                    errors = []
                    processed_users = []  # Track the users processed in this CSV
                    
                    # Process each row in the CSV
                    for index, row in df.iterrows():
                        try:
                            roll_no = str(row['roll_no']).strip()
                            email_id = str(row['email_id']).strip()
                            password = str(row['password']).strip()
                            mentor_id = str(row['mentor_id']).strip()
                            
                            # Check if the roll number format is valid
                            try:
                                validate_roll_no(roll_no)
                            except ValidationError as ve:
                                raise Exception(f"Invalid roll number format: {str(ve)}")
                            
                            # Create or update user accounts
                            user, created = User.objects.get_or_create(
                                username=roll_no,
                                defaults={'email': email_id}
                            )
                            
                            # Add user to the list of processed users
                            processed_users.append(user)
                            
                            # Set or update the password
                            user.set_password(password)
                            user.save()
                            
                            # Check if a student with this roll number exists
                            student = Student.objects.filter(roll_number=roll_no).first()
                            
                            if student:
                                # Link the user to the existing student if not already linked
                                if not student.user or student.user != user:
                                    student.user = user
                                    student.save()
                                    linked_count += 1
                                # Update student email if different
                                if student.email_id != email_id:
                                    student.email_id = email_id
                                    student.save()
                                    updated_count += 1
                                # Update mentor if missing or different
                                if student.mentor_id_id != mentor_id:
                                    student.mentor_id_id = mentor_id
                                    student.save()
                                    updated_count += 1
                            else:
                                # Create a new student record with minimal information
                                try:
                                    # Extract name from email if possible
                                    name_from_email = email_id.split('@')[0].replace('.', ' ').title()
                                    
                                    # Create a new student with just the required fields
                                    new_student = Student.objects.create(
                                        roll_number=roll_no,
                                        name="Unregistered Student",  
                                        email_id=email_id,
                                        user=user,
                                        mentor_id_id=mentor_id  # Use mentor_id_id for ForeignKey
                                    )
                                    student_created_count += 1
                                except Exception as se:
                                    raise Exception(f"Failed to create student record: {str(se)}")
                            
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                                
                        except Exception as e:
                            error_count += 1
                            errors.append(f"Error on row {index+1}: {str(e)}")
                    
                    # Associate processed users with this CSV file
                    csv_input.associated_users.add(*processed_users)
                    
                    # Mark the CSV as processed
                    csv_input.processed = True
                    csv_input.save()
                    
                    # Provide feedback to the user
                    if created_count > 0:
                        messages.success(request, f"Created {created_count} new user accounts successfully.")
                    if student_created_count > 0:
                        messages.success(request, f"Created {student_created_count} new student records successfully.")
                    if updated_count > 0:
                        messages.success(request, f"Updated {updated_count} existing accounts successfully.")
                    if linked_count > 0:
                        messages.success(request, f"Linked {linked_count} user accounts to student records.")
                    if error_count > 0:
                        messages.error(request, f"Encountered {error_count} errors during processing.")
                        for error in errors:  # Show all errors for better debugging
                            messages.error(request, error)
                            
                    return redirect('core:upload_csv')
                except Exception as e:
                    messages.error(request, f"Error processing CSV file: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error uploading file: {str(e)}")
        else:
            # Display all form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = upload_CSVForm()
    
    # Get the uploaded file for display (limit to one)
    recent_upload = CSVInput.objects.first() if CSVInput.objects.exists() else None
    
    return render(request, 'core/admin_view.html', {
        'form': form,
        'recent_upload': recent_upload
    })

@admin_required
def delete_csv(request, file_id):
    try:
        csv_file = CSVInput.objects.get(id=file_id)
        file_name = csv_file.file_name  # Get the filename from our stored field
        
        # Get all associated users before deleting
        associated_users = list(csv_file.associated_users.all())
        user_count = len(associated_users)
        
        # Delete student records linked to these users
        student_count = 0
        for user in associated_users:
            try:
                student = Student.objects.filter(user=user).first()
                if student:
                    # Unlink the user from student instead of deleting the student
                    student.user = None
                    student.save()
                    student_count += 1
            except Exception as e:
                messages.warning(request, f"Error unlinking student from user {user.username}: {str(e)}")
                
        # Delete all associated user accounts    
        for user in associated_users:
            try:
                user.delete()
            except Exception as e:
                messages.warning(request, f"Error deleting user {user.username}: {str(e)}")
        
        # Delete the database record (no file to delete from disk anymore)
        csv_file.delete()
        
        success_message = f"File '{file_name}' has been deleted successfully."
        if user_count > 0:
            success_message += f" {user_count} associated user accounts were deleted."
        if student_count > 0:
            success_message += f" {student_count} student records were unlinked from their user accounts."
            
        messages.success(request, success_message)
    except CSVInput.DoesNotExist:
        messages.error(request, "File not found.")
    except Exception as e:
        messages.error(request, f"Error deleting file: {str(e)}")
    
    return redirect('core:upload_csv')

@admin_required
def upload_csv_mentors(request):
    # Check if a file already exists - limit to one upload at a time
    existing_files = CSVInput_Mentors.objects.all()
    if existing_files.exists() and request.method == 'POST':
        messages.warning(request, "You already have an uploaded mentor file. Please delete it before uploading a new one.")
        form = Upload_CSVForm_Mentors()
    elif request.method == 'POST':
        form = Upload_CSVForm_Mentors(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the uploaded file
                csv_file = form.cleaned_data['csv_file']
                
                # Read the file content
                file_content = csv_file.read().decode('utf-8')
                
                # Save the CSV content to the database
                csv_input = CSVInput_Mentors.objects.create(
                    file_name=csv_file.name,
                    csv_content=file_content
                )
                
                # Confirm file upload success
                messages.success(request, f"Mentor file '{csv_file.name}' uploaded successfully!")
                
                try:
                    # Filter out comments (lines starting with //)
                    filtered_content = "\n".join(line for line in file_content.splitlines() if not line.startswith("//"))
                    filtered_file = io.StringIO(filtered_content)
                    df = pd.read_csv(filtered_file)
                    
                    # Display the first few rows for debugging
                    messages.success(request, f"Mentor CSV contains {len(df)} rows with columns: {', '.join(df.columns)}")
                    
                    # Keep track of stats for feedback
                    created_count = 0
                    updated_count = 0
                    linked_count = 0
                    mentor_created_count = 0
                    error_count = 0
                    errors = []
                    processed_users = []  # Track the users processed in this CSV
                    
                    # Process each row in the CSV
                    for index, row in df.iterrows():
                        try:
                            mentor_id = str(row['mentor_id']).strip()
                            name = str(row['name']).strip()
                            email_id = str(row['email_id']).strip()
                            password = str(row['password']).strip()
                            
                            # Create or update user accounts
                            user, created = User.objects.get_or_create(
                                username=mentor_id,
                                defaults={'email': email_id}
                            )
                            
                            # Add user to the list of processed users
                            processed_users.append(user)
                            
                            # Set or update the password
                            user.set_password(password)
                            user.save()
                            
                            # Check if a mentor with this ID exists
                            mentor = Mentor.objects.filter(mentor_id=mentor_id).first()
                            
                            if mentor:
                                # Link the user to the existing mentor if not already linked
                                if not mentor.user or mentor.user != user:
                                    mentor.user = user
                                    mentor.save()
                                    linked_count += 1
                                # Update mentor email and name if different
                                if mentor.email != email_id or mentor.name != name:
                                    mentor.email = email_id
                                    mentor.name = name
                                    mentor.save()
                                    updated_count += 1
                            else:
                                # Create a new mentor record
                                try:
                                    new_mentor = Mentor.objects.create(
                                        mentor_id=mentor_id,
                                        name=name,
                                        email=email_id,
                                        user=user
                                    )
                                    mentor_created_count += 1
                                except Exception as me:
                                    raise Exception(f"Failed to create mentor record: {str(me)}")
                            
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                                
                        except Exception as e:
                            error_count += 1
                            errors.append(f"Error on row {index+1}: {str(e)}")
                    
                    # Associate processed users with this CSV file
                    csv_input.associated_users.add(*processed_users)
                    
                    # Mark the CSV as processed
                    csv_input.processed = True
                    csv_input.save()
                    
                    # Provide feedback to the user
                    if created_count > 0:
                        messages.success(request, f"Created {created_count} new user accounts successfully.")
                    if mentor_created_count > 0:
                        messages.success(request, f"Created {mentor_created_count} new mentor records successfully.")
                    if updated_count > 0:
                        messages.success(request, f"Updated {updated_count} existing accounts successfully.")
                    if linked_count > 0:
                        messages.success(request, f"Linked {linked_count} user accounts to mentor records.")
                    if error_count > 0:
                        messages.error(request, f"Encountered {error_count} errors during processing.")
                        for error in errors:  # Show all errors for better debugging
                            messages.error(request, error)
                            
                    return redirect('core:upload_csv')
                except Exception as e:
                    messages.error(request, f"Error processing mentor CSV file: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error uploading mentor file: {str(e)}")
        else:
            # Display all form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = Upload_CSVForm_Mentors()
    
    # Get the uploaded file for display (limit to one)
    recent_upload = CSVInput_Mentors.objects.first() if CSVInput_Mentors.objects.exists() else None
    student_form = upload_CSVForm()
    student_upload = CSVInput.objects.first() if CSVInput.objects.exists() else None
    
    return render(request, 'core/admin_view.html', {
        'mentor_form': form,
        'form': student_form,
        'recent_upload': student_upload,
        'mentor_upload': recent_upload
    })

@admin_required
def delete_csv_mentors(request, file_id):
    try:
        csv_file = CSVInput_Mentors.objects.get(id=file_id)
        file_name = csv_file.file_name  # Get the filename from our stored field
        
        # Get all associated users before deleting
        associated_users = list(csv_file.associated_users.all())
        user_count = len(associated_users)
        
        # Delete mentor records linked to these users
        mentor_count = 0
        for user in associated_users:
            try:
                mentor = Mentor.objects.filter(user=user).first()
                if mentor:
                    # Unlink the user from mentor instead of deleting the mentor
                    mentor.user = None
                    mentor.save()
                    mentor_count += 1
            except Exception as e:
                messages.warning(request, f"Error unlinking mentor from user {user.username}: {str(e)}")
                
        # Delete all associated user accounts    
        for user in associated_users:
            try:
                user.delete()
            except Exception as e:
                messages.warning(request, f"Error deleting user {user.username}: {str(e)}")
        
        # Delete the database record
        csv_file.delete()
        
        success_message = f"Mentor file '{file_name}' has been deleted successfully."
        if user_count > 0:
            success_message += f" {user_count} associated user accounts were deleted."
        if mentor_count > 0:
            success_message += f" {mentor_count} mentor records were unlinked from their user accounts."
            
        messages.success(request, success_message)
    except CSVInput_Mentors.DoesNotExist:
        messages.error(request, "File not found.")
    except Exception as e:
        messages.error(request, f"Error deleting file: {str(e)}")
    
    return redirect('core:upload_csv')

def student_detail(request, student_id):
    return render(request, 'core/student_detail.html', {
        'student_id': student_id,
        'user': request.user
    })

@login_required
def student_registration_form(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # Process the form data - save to the database
            student = request.user.student
            for field, value in form.cleaned_data.items():
                setattr(student, field, value)
            student.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('student_dashboard')  # Redirect to dashboard after form submission
    else:
        # Pre-fill the form with existing data if available
        initial_data = {}
        if hasattr(request.user, 'student'):
            student = request.user.student
            for field in StudentRegistrationForm().fields:
                if hasattr(student, field):
                    initial_data[field] = getattr(student, field)
        form = StudentRegistrationForm(initial=initial_data)
    
    return render(request, 'core/student_form.html', {'form': form})
