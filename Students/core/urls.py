from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('mentor/dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('upload_csv_mentors/', views.upload_csv_mentors, name='upload_csv_mentors'),
    path('delete_csv/<int:file_id>/', views.delete_csv, name='delete_csv'),
    path('delete_csv_mentors/<int:file_id>/', views.delete_csv_mentors, name='delete_csv_mentors'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/form/', views.student_registration_form, name='student_form'),
]
