from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from projects import models
from accounts import models
from .models import Project, Task, Comment
from .forms import TaskForm, CommentForm, ProjectUpdateForm
from accounts.decorators import admin_required, manager_required, user_required
from accounts.mixins import AdminRequiredMixin, ManagerRequiredMixin, UserRequiredMixin


class ProjectListView(UserRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        user = self.request.user
        return Project.objects.all()


class ProjectDetailView(UserRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
        context['can_add_tasks'] = self.can_user_add_tasks()
        return context

    def can_user_add_tasks(self):
        user = self.request.user
        return (user.is_authenticated and
                (user.is_admin() or
                 user.is_manager() or
                 self.object.managers.filter(id=user.id).exists()))


class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'managers', 'users']
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Проект успешно создан')
        return super().form_valid(form)


class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectUpdateForm  # Используем кастомную форму
    template_name = 'projects/project_form.html'
    # fields = ['title', 'description', 'managers', 'users']
    success_url = reverse_lazy('projects:project_list')

    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Project.objects.all()
        return Project.objects.filter(managers=user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Проект успешно обновлен')
        return super().form_valid(form)


class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Проект успешно удален')
        return super().delete(request, *args, **kwargs)


# Task Views
class TaskDetailView(UserRequiredMixin, DetailView):
    model = Task
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class TaskCreateView(ManagerRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.id})

    def get_initial(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return {'project': project}

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        if not (self.request.user.is_admin() or project.managers.filter(id=self.request.user.id).exists()):
            raise PermissionDenied
        form.instance.project = project
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Задача успешно создана')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()  # Убедитесь, что этот метод существует
        return kwargs

    def get_project(self):
        return get_object_or_404(Project, id=self.kwargs['project_id'])


class TaskUpdateView(ManagerRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'

    def get_success_url(self):
        return reverse_lazy('projects:task_detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        user = self.request.user
        if user.is_admin():
            return Task.objects.all()
        return Task.objects.filter(project__managers=user)

    def form_valid(self, form):
        messages.success(self.request, 'Задача успешно обновлена')
        return super().form_valid(form)


@user_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Проверяем, что пользователь имеет доступ к задаче
    if not (request.user.is_admin() or
            request.user in task.project.managers.all() or
            request.user in task.project.users.all() or
            task.assigned_to == request.user):
        return HttpResponseForbidden("Доступ запрещен: недостаточно прав")

    task.is_completed = not task.is_completed
    task.save()

    messages.success(request, f'Задача {"завершена" if task.is_completed else "возобновлена"}')
    return redirect('projects:task_detail', pk=task.pk)


@user_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    # Проверяем доступ к задаче
    if not (request.user.is_admin() or
            request.user in task.project.managers.all() or
            request.user in task.project.users.all()):
        return HttpResponseForbidden("Доступ запрещен: недостаточно прав")

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен')
            return redirect('projects:task_detail', pk=task.pk)
    else:
        form = CommentForm()

    return render(request, 'projects/task_detail.html', {
        'task': task,
        'comment_form': form
    })
