from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.urls import reverse
from .decorators import student_required, mentor_required, admin_required
from .forms import upload_CSVForm
from .models import Student, Mentor, CSVInput
from django.contrib.auth.models import User
import pandas as pd
import os

# Create your views here.
@login_required
def home(request):
    return render(request, 'core/home.html', {
        'user': request.user
    })

@student_required
def student_dashboard(request):
    # Get student data
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
        'user': request.user
    }
    return render(request, 'core/student_dashboard.html', context)

@mentor_required
def mentor_dashboard(request):
    # Get mentor data and assigned students
    mentor = Mentor.objects.get(user=request.user)
    students = Student.objects.filter(mentor=mentor)
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
                
                # Save the file to the CSVInput model
                csv_input = CSVInput.objects.create(file=csv_file)
                
                # Confirm file upload success
                messages.success(request, f"File '{csv_file.name}' uploaded successfully!")
                
                try:
                    # Read the file with pandas
                    df = pd.read_csv(csv_file)
                    
                    # Display the first few rows for debugging
                    messages.info(request, f"CSV contains {len(df)} rows with columns: {', '.join(df.columns)}")
                    
                    # Keep track of stats for feedback
                    created_count = 0
                    updated_count = 0
                    error_count = 0
                    errors = []
                    
                    # Process each row in the CSV
                    for index, row in df.iterrows():
                        try:
                            roll_no = str(row['roll_no']).strip()
                            email_id = str(row['email_id']).strip()
                            password = str(row['password']).strip()
                            
                            # Check if the roll number format is valid
                            try:
                                validate_roll_no(roll_no)
                            except ValidationError as ve:
                                raise Exception(f"Invalid roll number format: {str(ve)}")
                            
                            # Check if a student with this roll number already exists
                            student, created = Student.objects.get_or_create(
                                roll_number=roll_no,
                                defaults={'email_id': email_id}
                            )
                            
                            # Create or update the user
                            if student.user:
                                # User exists, update password if needed
                                user = student.user
                                user.set_password(password)
                                user.save()
                                updated_count += 1
                            else:
                                # Create new user
                                username = roll_no  # Using roll number as username
                                user = User.objects.create_user(
                                    username=username,
                                    email=email_id,
                                    password=password
                                )
                                # Link user to student
                                student.user = user
                                student.save()
                                created_count += 1
                        
                        except Exception as e:
                            error_count += 1
                            errors.append(f"Error on row {index+1}: {str(e)}")
                    
                    # Mark the CSV as processed
                    csv_input.processed = True
                    csv_input.save()
                    
                    # Provide feedback to the user
                    if created_count > 0:
                        messages.success(request, f"Created {created_count} new student accounts successfully.")
                    if updated_count > 0:
                        messages.success(request, f"Updated {updated_count} existing student accounts successfully.")
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
        file_name = csv_file.file.name.split('/')[-1]  # Extract just the filename
        
        # Delete the file from storage
        if csv_file.file:
            if os.path.isfile(csv_file.file.path):
                os.remove(csv_file.file.path)
        
        # Delete the database record
        csv_file.delete()
        
        messages.success(request, f"File '{file_name}' has been deleted successfully.")
    except CSVInput.DoesNotExist:
        messages.error(request, "File not found.")
    except Exception as e:
        messages.error(request, f"Error deleting file: {str(e)}")
    
    return redirect('core:upload_csv')

