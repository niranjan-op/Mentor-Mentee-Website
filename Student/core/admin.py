from django.contrib import admin
from .models import (
    Branch, Division, Mentor, Student,
    Subject, ElectiveGroup, StudentSubject,
    InternalAssessment, EndSemesterExam,
    Project, SemesterResult
)

# Register your models here.
admin.site.register(Branch)
admin.site.register(Division)
admin.site.register(Mentor)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(ElectiveGroup)
admin.site.register(StudentSubject)
admin.site.register(InternalAssessment)
admin.site.register(EndSemesterExam)
admin.site.register(Project)
admin.site.register(SemesterResult)
