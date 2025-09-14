from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active',)
    list_filter = ['email', 'is_active']

