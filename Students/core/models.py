from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_roll_no, validate_email, validate_dob
from django.contrib.auth.models import User
import os

class Branch(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=10)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='divisions')
    
    def __str__(self):
        return f"{self.name}"  # Simplified

class Mentor(models.Model):
    mentor_id = models.CharField(max_length=8, primary_key=True, unique=True)
    name = models.CharField(max_length=100, help_text="Enter your full name in the format 'First Middle Last'")
    email = models.EmailField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='mentor_profile')
    
    def __str__(self):
        return self.name  # Simplified

class Student(models.Model):
    INTERNSHIP_STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('ACCEPTED', 'Accepted'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]
    
    roll_number = models.CharField(max_length=8, primary_key=True, unique=True, validators=[validate_roll_no])
    name = models.CharField(max_length=100, help_text="Enter your full name in the format 'First Middle Last'")
    email_id = models.EmailField(max_length=100, validators=[validate_email])
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    
    # Make these fields optional by adding null=True, blank=True
    address = models.TextField(max_length=500, help_text="Enter your full address", null=True, blank=True)
    phone_no_student = models.CharField(max_length=12, help_text="Enter your phone number", null=True, blank=True)
    phone_no_mother = models.CharField(max_length=12, help_text="Enter your mother's phone number", null=True, blank=True)
    phone_no_father = models.CharField(max_length=12, help_text="Enter your father's phone number", null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    dob = models.DateField(validators=[validate_dob], help_text="Enter your date of birth in the format YYYY-MM-DD", null=True, blank=True)
    
    # Academic records
    marks_10th = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                    validators=[MinValueValidator(0), MaxValueValidator(100)],
                                    help_text="Enter percentage marks (0-100)")
    marks_12th = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    validators=[MinValueValidator(0), MaxValueValidator(100)],
                                    help_text="Enter percentage marks (0-100)")
    jee_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   help_text="Enter percentile (0-100)")
    cet_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   help_text="Enter percentile (0-100)")
    
    # Professional development
    internship_status = models.CharField(max_length=20, choices=INTERNSHIP_STATUS_CHOICES, default='NOT_STARTED')
    internship_company = models.CharField(max_length=100, blank=True, null=True)
    internship_role = models.CharField(max_length=100, blank=True, null=True)
    mentor_id = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    
    # Personal development tracking
    goals = models.TextField(blank=True, help_text="Student's academic and career goals")
    strengths = models.TextField(blank=True, help_text="Student's identified strengths")
    weaknesses = models.TextField(blank=True, help_text="Areas for improvement")
    achievements = models.TextField(blank=True, help_text="Notable achievements during the semester")
    extracurricular = models.TextField(blank=True, help_text="Extracurricular activities and participation")
    suggestions = models.TextField(blank=True, help_text="Mentor suggestions for improvement")
    
    def __str__(self):
        return self.name  # Simplified

class Subject(models.Model):
    name = models.CharField(max_length=100)
    semester = models.PositiveIntegerField()  # Add this line back
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='subjects')
    subject_code = models.CharField(max_length=10, unique=True)
    is_elective = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name  # Simplified

class ElectiveGroup(models.Model):
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='elective_groups')
    subjects = models.ManyToManyField(Subject, related_name='elective_groups')
    
    def __str__(self):
        return self.name  # Simplified

class SemesterResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semester_results')
    semester = models.PositiveIntegerField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True,
                             validators=[MinValueValidator(0), MaxValueValidator(10)],
                             help_text="Semester GPA (0-10 scale)")
    average_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)],
                                           help_text="Average percentage across all subjects")
    
    class Meta:
        unique_together = ('student', 'semester')
    
    def __str__(self):
        return f"Semester {self.semester}"  # Simplified

class StudentSubject(models.Model):
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.PositiveIntegerField()
    is_elective = models.BooleanField(default=False)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'semester')
    
    def __str__(self):
        return f"Subject - Sem {self.semester}"  # Simplified

class InternalAssessment(models.Model):
    ASSESSMENT_TYPES = [
        ('IA1', 'Internal Assessment 1'),
        ('IA2', 'Internal Assessment 2'),
    ]
    
    student_subject = models.ForeignKey(StudentSubject, on_delete=models.CASCADE, related_name='internal_assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('student_subject', 'assessment_type')
    
    def __str__(self):
        return self.assessment_type  # Simplified

class EndSemesterExam(models.Model):
    student_subject = models.OneToOneField(StudentSubject, on_delete=models.CASCADE, related_name='end_semester_exam')
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=80.00)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return "End Sem"  # Simplified

class Project(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    semester = models.PositiveIntegerField()
    technologies = models.CharField(max_length=200, blank=True)
    repository_link = models.URLField(blank=True, null=True)
    grade = models.CharField(max_length=2, blank=True, null=True)
    
    def __str__(self):
        return self.title  # Simplified

class CSVInput(models.Model):
    file_name = models.CharField(max_length=255)  # Store the original filename
    csv_content = models.TextField()  # Store the CSV content directly in the database
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    # Track users created/updated from this CSV file
    associated_users = models.ManyToManyField(User, blank=True, related_name='source_csv_files')
    
    def __str__(self):
        return f"CSV Upload {self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "CSV Upload"
        verbose_name_plural = "CSV Uploads"
        ordering = ['-uploaded_at']
class CSVInput_Mentors(models.Model):
    file_name=models.CharField(max_length=255)
    csv_content=models.TextField()
    uploaded_at=models.DateTimeField(auto_now_add=True)
    processed=models.BooleanField(default=False)
    associated_users=models.ManyToManyField(User, blank=True, related_name='source_csv_files_mentors')
    def __str__(self):
        return f"CSV Upload {self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"