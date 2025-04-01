from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/student/', views.student_login, name='student_login'),
    path('login/mentor/', views.mentor_login, name='mentor_login'),
    path('logout/', views.logout_view, name='logout'),
]