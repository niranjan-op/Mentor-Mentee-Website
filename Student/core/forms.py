from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
from django.core.files.storage import FileSystemStorage

class upload_CSVForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File", help_text="Upload a CSV file containing student data.")
    
    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if not file.name.endswith('.csv'):
            raise ValidationError("File type is not supported. Please upload a CSV file.")
        return file
    
    def clean(self):    
        cleaned_data = super().clean()
        csv_file = cleaned_data.get('csv_file')
        
        if not csv_file:
            raise ValidationError("This field is required.")
        
        # Read the first few lines to check format
        try:
            # Read file content and check for comment markers
            csv_file.seek(0)
            first_line = csv_file.readline().decode('utf-8').strip()
            if first_line.startswith('//') or first_line.startswith('#'):
                raise ValidationError("CSV file contains comment markers. Remove // or # from the beginning of the file.")
            
            # Reset file pointer
            csv_file.seek(0)
            
            # Try parsing with pandas
            df = pd.read_csv(csv_file)
            
            if df.empty:
                raise ValidationError("The CSV file is empty. Please upload a valid CSV file with data.")
                
            required_columns=['roll_no','email_id','password']
            
            if not all(col in [column.lower() for column in df.columns] for col in required_columns):
                raise ValidationError("CSV file must contain the following columns: roll_no, email_id, password. Please note that the column names are case sensitive.")
            elif df.isnull().values.any():
                raise ValidationError("The CSV file contains null values. Please ensure all fields are filled.")
            elif df.duplicated(subset=['roll_no']).any():
                raise ValidationError("The CSV file contains duplicate roll numbers. Please ensure all roll numbers are unique.")
            elif df.duplicated(subset=['email_id']).any():
                raise ValidationError("The CSV file contains duplicate email IDs. Please ensure all email IDs are unique.")
        
        except pd.errors.EmptyDataError:
            raise ValidationError("The CSV file is empty or has an invalid format.")
        except pd.errors.ParserError:
            raise ValidationError("Could not parse the CSV file. Make sure it's a valid CSV format without comment markers or special characters at the beginning.")
            
        # Reset the file pointer to the beginning so it can be read again in the view
        csv_file.seek(0)
        
        return cleaned_data