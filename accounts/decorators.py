from django.contrib import messages
from django.http import HttpResponseForbidden, request
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


def role_required(allowed_roles):
    """
    Декоратор для проверки роли пользователя
    """

    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Доступ запрещен: недостаточно прав")

        return _wrapped_view

    return decorator


def admin_required(view_func):
    """Декоратор для доступа только администраторам"""
    return role_required(['admin'])(view_func)


def manager_required(view_func):
    """Декоратор для доступа менеджерам и администраторам"""
    return role_required(['admin', 'manager'])(view_func)


def user_required(view_func):
    """Декоратор для доступа всем авторизованным пользователям"""
    return role_required(['admin', 'manager', 'user'])(view_func)

'''
# Миксины для класс-базированных представлений
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin()

    def handle_no_permission(self):
        return HttpResponseForbidden("Доступ запрещен: недостаточно прав")
        #return redirect('accounts:login')


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin() or self.request.user.is_manager()

    def handle_no_permission(self):
        return HttpResponseForbidden("Доступ запрещен: недостаточно прав")
      #  return redirect('accounts:login')


class UserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        return HttpResponseForbidden("Доступ запрещен: необходимо авторизоваться")
        #return redirect('accounts:login')
'''

