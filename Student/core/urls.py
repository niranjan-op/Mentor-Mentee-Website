from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('mentor/dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('delete_csv/<int:file_id>/', views.delete_csv, name='delete_csv'),
]
