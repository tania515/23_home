from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):  # пользователь
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):  # суперпользователь
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser,  PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        MANAGER = 'manager', _('Менеджер')
        USER = 'user', _('Пользователь')

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=30, verbose_name='Имя', blank=True)
    last_name = models.CharField(max_length=30, verbose_name='Фамилия', blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль'
    )

    is_active = models.BooleanField(default=True, verbose_name='Аккаунт активен')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ("can_manage_users", "Может управлять пользователями"),
            ("can_manage_projects", "Может управлять проектами"),
            ("can_edit_tasks", "Может редактировать задачи"),
            ("can_view_projects", "Может просматривать проекты"),
            ("can_add_comments", "Может добавлять комментарии"),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_manager(self):
        return self.role == self.Role.MANAGER

    def is_regular_user(self):
        return self.role == self.Role.USER

    def can_manage_users(self):
        return self.is_admin()

    def can_manage_projects(self):
        return self.is_admin() or self.is_manager()

    def can_edit_tasks(self):
        return self.is_admin() or self.is_manager()

    def can_view_projects(self):
        return True

    def can_add_comments(self):
        return True

