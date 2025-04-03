from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
import io
from django.core.files.storage import FileSystemStorage
from .models import Student, Branch, Division
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_roll_no, validate_email, validate_dob


class upload_CSVForm(forms.Form):
    csv_file = forms.FileField(
        label="Upload CSV File", 
        help_text="Upload a CSV file with columns: roll_no, email_id, password, mentor_id to create or update student user accounts."
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if not file.name.endswith('.csv'):
            raise ValidationError("File type is not supported. Please upload a CSV file.")
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        csv_file = cleaned_data.get('csv_file')
        
        if not csv_file:
            return cleaned_data
        
        try:
            # Reset file pointer to the beginning
            csv_file.seek(0)
            
            file_content = csv_file.read().decode('utf-8')
            # Remove lines starting with "//"
            filtered_content = "\n".join(line for line in file_content.splitlines() if not line.startswith("//"))
            filtered_file = io.StringIO(filtered_content)
            df = pd.read_csv(filtered_file)
            
            if df.empty:
                raise ValidationError("The CSV file is empty. Please upload a valid CSV file with data.")
            
            required_columns = ['roll_no', 'email_id', 'password','mentor_id']
            missing_columns = [col for col in required_columns if col not in [column.lower() for column in df.columns]]
            
            if missing_columns:
                raise ValidationError(f"CSV file is missing required columns: {', '.join(missing_columns)}. Please ensure all required columns are present.")
                
            if df.isnull().values.any():
                raise ValidationError("The CSV file contains null values. Please ensure all fields are filled.")
                
            if df.duplicated(subset=['roll_no']).any():
                raise ValidationError("The CSV file contains duplicate roll numbers. Please ensure all roll numbers are unique.")
                
            if df.duplicated(subset=['email_id']).any():
                raise ValidationError("The CSV file contains duplicate email IDs. Please ensure all email IDs are unique.")
            
            # Reset file pointer for later use
            csv_file.seek(0)
            
        except pd.errors.EmptyDataError:
            raise ValidationError("The CSV file is empty or has an invalid format.")
        except pd.errors.ParserError:
            raise ValidationError("Could not parse the CSV file. Make sure it's a valid CSV format without unexpected characters.")
        
        return cleaned_data

class Upload_CSVForm_Mentors(forms.Form):
    csv_file = forms.FileField(
        label="Upload CSV File for Mentors", 
        help_text="Upload a CSV file with columns: mentor_id, name, email_id, password to create or update mentor user accounts."
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if not file.name.endswith('.csv'):
            raise ValidationError("File type is not supported. Please upload a CSV file.")
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        csv_file = cleaned_data.get('csv_file')
        
        if not csv_file:
            return cleaned_data
        
        try:
            # Reset file pointer to the beginning
            csv_file.seek(0)
            
            file_content = csv_file.read().decode('utf-8')
            # Remove lines starting with "//"
            filtered_content = "\n".join(line for line in file_content.splitlines() if not line.startswith("//"))
            filtered_file = io.StringIO(filtered_content)
            df = pd.read_csv(filtered_file)
            
            if df.empty:
                raise ValidationError("The CSV file is empty. Please upload a valid CSV file with data.")
            
            required_columns = ['mentor_id', 'name', 'email_id', 'password']
            missing_columns = [col for col in required_columns if col not in [column.lower() for column in df.columns]]
            
            if missing_columns:
                raise ValidationError(f"CSV file is missing required columns: {', '.join(missing_columns)}. Please ensure all required columns are present.")
                
            if df.isnull().values.any():
                raise ValidationError("The CSV file contains null values. Please ensure all fields are filled.")
                
            if df.duplicated(subset=['mentor_id']).any():
                raise ValidationError("The CSV file contains duplicate mentor IDs. Please ensure all mentor IDs are unique.")
                
            if df.duplicated(subset=['email_id']).any():
                raise ValidationError("The CSV file contains duplicate email IDs. Please ensure all email IDs are unique.")
            
            # Reset file pointer for later use
            csv_file.seek(0)
            
        except pd.errors.EmptyDataError:
            raise ValidationError("The CSV file is empty or has an invalid format.")
        except pd.errors.ParserError:
            raise ValidationError("Could not parse the CSV file. Make sure it's a valid CSV format without unexpected characters.")
        
        return cleaned_data

class StudentRegistrationForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': "Enter your full name in the format 'First Middle Last'"})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': "Enter your full address"}),
        max_length=500, 
        required=True
    )
    phone_no_student = forms.CharField(
        max_length=12, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': "Enter your phone number"})
    )
    phone_no_mother = forms.CharField(
        max_length=12, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': "Enter your mother's phone number"})
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(), 
        required=True
    )
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(), 
        required=True
    )
    dob = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'placeholder': "YYYY-MM-DD", 'type': 'date'}),
        validators=[validate_dob],
    )
    marks_10th = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'placeholder': "Enter percentage marks (0-100)"})
    )
    marks_12th = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'placeholder': "Enter percentage marks (0-100)"})
    )
    jee_score = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'placeholder': "Enter percentile (0-100)"})
    )
    cet_score = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={'placeholder': "Enter percentile (0-100)"})
    )
    internship_status = forms.ChoiceField(
        choices=Student.INTERNSHIP_STATUS_CHOICES, 
        required=True
    )
    internship_company = forms.CharField(
        max_length=100, 
        required=False,  # Not required initially, validated in clean
        widget=forms.TextInput(attrs={
            'placeholder': "Enter the name of the company where you did your internship"
        })
    )
    internship_role = forms.CharField(
        max_length=100, 
        required=False,  # Not required initially, validated in clean
        widget=forms.TextInput(attrs={
            'placeholder': "Enter your role during the internship"
        })
    )
    goals = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': "Enter your goals for the internship"}), 
        max_length=500, 
        required=True
    )
    strengths = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': "Enter your strengths"}), 
        max_length=500, 
        required=True
    )
    weaknesses = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': "Enter your weaknesses"}), 
        max_length=500, 
        required=True
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': "Enter your skills relevant to the internship"}), 
        max_length=500, 
        required=True
    )
    achievements = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': "Enter your achievements"}), 
        max_length=500, 
        required=True
    )
    # suggestions = forms.CharField(
    #     widget=forms.Textarea(attrs={'placeholder': "Enter your suggestions for the internship program"}), 
    #     max_length=500, 
    #     required=True
    # )
    # IA Marks:
    
    
    def clean(self):
        cleaned_data = super().clean()
        internship_status = cleaned_data.get('internship_status')
        
        # Define which statuses require company and role information
        require_internship_details = ['SHORTLISTED', 'ACCEPTED', 'COMPLETED']
        
        if internship_status in require_internship_details:
            # If status requires details, validate that they are provided
            internship_company = cleaned_data.get('internship_company')
            if not internship_company:
                self.add_error('internship_company', 
                               "Company name is required when internship status is Shortlisted, Accepted, or Completed")
            
            internship_role = cleaned_data.get('internship_role')
            if not internship_role:
                self.add_error('internship_role',
                               "Role is required when internship status is Shortlisted, Accepted, or Completed")
        
        return cleaned_data


