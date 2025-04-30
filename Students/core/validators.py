import re
from django.core.exceptions import ValidationError
from datetime import datetime, date
from datetime import timedelta

def validate_roll_no(roll_number):
    pattern = r'^[0-9]{3}[A-Z]{1}[0-9]{4}$'
    if not re.match(pattern, roll_number):
        # More descriptive error message
        raise ValidationError(f'Roll number "{roll_number}" must be in the format 123A1234 (3 digits, 1 uppercase letter, 4 digits)')
    return roll_number

def validate_email(email):
    # Check if the email ends with the expected domain
    if not email.endswith('@gst.sies.edu.in'):
        raise ValidationError('Email must end with @gst.sies.edu.in')
    
    # Optional: Add additional checks if needed
    # For example, we could check if the username contains at least 3 characters
    username = email.split('@')[0]
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long')
    
    return email

def validate_dob(dob):
    today = date.today()
    
    # Convert datetime to date if needed
    if isinstance(dob, datetime):
        dob = dob.date()
    
    # Check if date is in the future
    if dob > today:
        raise ValidationError('Date of birth cannot be in the future.')
    
    # Check if year is valid
    if dob.year < 1900:
        raise ValidationError('Year of birth cannot be before 1900.')
    
    # Check age (at least 18 years old)
    min_birth_date = today - timedelta(days=365.25 * 18)
    if dob > min_birth_date:
        raise ValidationError('You must be at least 18 years old.')
    
    return dob