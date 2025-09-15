from django import forms

from accounts import models
from accounts.models import CustomUser
from .models import Task, Comment, Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project:
            # Ограничиваем выбор только участниками проекта
            self.fields['assigned_to'].queryset = self.project.get_all_members()

    def clean_assigned_to(self):
        assigned_to = self.cleaned_data.get('assigned_to')
        if assigned_to and self.project and not self.project.is_member(assigned_to):
            raise forms.ValidationError("Выбранный пользователь не является участником проекта")
        return assigned_to


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Напишите ваш комментарий...'}),
        }


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'managers', 'users']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Фильтруем менеджеров - только администраторы и менеджеры
        self.fields['managers'].queryset = CustomUser.objects.filter(
            models.Q(role='admin') | models.Q(role='manager')
        )

        # Фильтруем обычных пользователей - исключаем администраторов
        self.fields['users'].queryset = CustomUser.objects.exclude(role='admin')

        # Делаем виджеты более удобными
        self.fields['managers'].widget = forms.CheckboxSelectMultiple()
        self.fields['users'].widget = forms.CheckboxSelectMultiple()
