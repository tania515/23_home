from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
   path('register/', views.register, name='register'),
   path('login/', views.login, name='login'),
   path('logout/', views.logout, name='logout'),
   path('profile/', views.profile, name='profile'),
   path('password-reset/', views.password_reset_request, name='password_reset'),
   path('password-reset-confirm/<uidb64>/<token>/',
        views.password_reset_confirm,
        name='password_reset_confirm'),
   path('profile/change-password/', views.change_password, name='change_password'),
   path('dashboard/', views.dashboard_view, name='dashboard'),
   path('admin/users/', views.user_management_view, name='user_management'),
  # path('admin/users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
]