from django.contrib import admin
from .models import Project, Task, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'updated_at']
    list_filter = ['created_at', 'managers']
    search_fields = ['title', 'description']
    filter_horizontal = ['managers', 'users']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'created_at', 'project']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'task', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__email']
    readonly_fields = ['created_at']