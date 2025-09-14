from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            return HttpResponseForbidden("Доступ запрещен: недостаточно прав")
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_admin() or request.user.is_manager()):
            return HttpResponseForbidden("Доступ запрещен: недостаточно прав")
        return super().dispatch(request, *args, **kwargs)


class UserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'У вас нет прав для доступа к этой странице. Пожалуйста, авторизуйтесь.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

