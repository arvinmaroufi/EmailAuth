from django.urls import path
from . import views


app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login-username/', views.username_login, name='username_login'),
    path('login-email/', views.email_login, name='email_login'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]
