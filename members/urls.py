from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),  
    path("contact/", views.contact, name="contact"),
    path("teacher_dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path('attendance/', views.attendance, name='attendance'),
    path('profile/', views.profile, name='profile'),
   
    
]

