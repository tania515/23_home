from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, \
    PasswordChangeForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='Имя')
    last_name = forms.CharField(required=True, label='Фамилия')
    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        label='Роль',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class CustomUserLoginForm(AuthenticationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'autocomplete': 'username email',
            'class': 'form-control',
            'placeholder': 'Введите ваш email',
            'autofocus': True,
            'name': 'email',
            'id': 'email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль',
            'name': 'password',
            'id': 'password'
        })
    )

    field_order = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)  # Полностью удаляем поле username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email обязателен")

        # Проверяем, есть ли пользователь с таким email
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email не найден")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("Пароль обязателен")
        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Пробуем аутентифицировать
            self.user_cache = authenticate(
                request=self.request,
                email=email,
                password=password
            )

            # Если аутентификация не удалась
            if not self.user_cache:
                # Проверяем существует ли пользователь
                user_exists = User.objects.filter(email=email).exists()

                if user_exists:
                    # Если существует, проверяем активность
                    user = User.objects.get(email=email)
                    if not user.is_active:
                        raise ValidationError("Аккаунт не активирован. Пожалуйста, проверьте вашу почту")
                    else:
                        raise ValidationError("Неверный пароль")
                else:
                    raise ValidationError("Пользователь с таким email не найден")

        return cleaned_data

    def get_user(self):
        return self.user_cache


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email',
            'autocomplete': 'email'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("Пользователь с таким email не найден")
        return email


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


