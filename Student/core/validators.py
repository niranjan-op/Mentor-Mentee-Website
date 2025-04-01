import re
from django.core.exceptions import ValidationError

def validate_roll_no(roll_number):
    pattern = r'^[0-9]{3}[A-Z]{1}[0-9]{4}$'
    if not re.match(pattern, roll_number):
        raise ValidationError('Roll number must be in the format 123A1234')
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
