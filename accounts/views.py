from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from projects.models import Project
from . import models
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomPasswordResetForm, \
    CustomSetPasswordForm, CustomPasswordChangeForm
from .decorators import admin_required, manager_required
from django.contrib import messages

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            return redirect('home')
        else:
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    auth_login(request, user)
                    messages.success(request, "Вы успешно авторизированы!")
                    return redirect('accounts:profile')
                else:
                    messages.error(request, "Что то не так (email, пароль или нет активации")
            except CustomUser.DoesNotExist:
                messages.error(request, "Пользователь не найден")
                return redirect('accounts:login')

        else:
            messages.error(request, "Исправьте ошибки в форме.")

    else:
        form = CustomUserLoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)

            # Генерация токена для сброса пароля
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = request.build_absolute_uri(
                f'/accounts/password-reset-confirm/{uid}/{token}/'
            )

            send_mail(
                'Сброс пароля',
                f'Для сброса пароля перейдите по ссылке: {reset_link}',
                'admin@shop.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Письмо с инструкциями по сбросу пароля отправлено на ваш email')
            return redirect('home')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        # Декодируем uid и получаем пользователя
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Проверяем токен
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ваш пароль успешно изменен!')
                return redirect('accounts:login')
        else:
            form = CustomSetPasswordForm(user)

        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Ссылка для сброса пароля недействительна или устарела.')
        return redirect('accounts:password_reset')


@login_required
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    messages.success(request, "Вы успешно вышли.")
    return redirect('home')


@login_required
def profile(request):
    user = request.user

    if user.is_admin:
        all_projects = Project.objects.all()
        user_projects = Project.objects.filter(
            models.Q(created_by=user) |
            models.Q(managers=user) |
            models.Q(users=user)
        ).distinct()
    else:
        all_projects = None
        user_projects = Project.objects.filter(
            models.Q(created_by=user) |
            models.Q(managers=user) |
            models.Q(users=user)
        ).distinct()

    return render(request, 'accounts/profile.html', {
        'user': user,
        'all_projects': all_projects,  # Только для админов
        'user_projects': user_projects  # Для всех пользователей
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def dashboard_view(request):
    # Разный контент в зависимости от роли
    context = {}
    if request.user.is_admin():
        context['admin_content'] = True
    elif request.user.is_manager():
        context['manager_content'] = True
    else:
        context['user_content'] = True

    return render(request, 'dashboard.html', context)


@admin_required
def user_management_view(request):
    users = CustomUser.objects.all()
    return render(request, 'admin/user_management.html', {'users': users})




