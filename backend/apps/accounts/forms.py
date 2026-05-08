from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm as BaseAuthenticationForm,
    UserCreationForm as BaseUserCreationForm,
    UserChangeForm as BaseUserChangeForm,
    PasswordChangeForm as BasePasswordChangeForm,
)
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from .models import User
from .permissions import PERMISSION_GROUPS, ALL_PERM_CODENAMES, ROLE_PRESETS


class LoginForm(BaseAuthenticationForm):
    username = forms.CharField(
        label=_('اسم المستخدم'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('أدخل اسم المستخدم'),
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label=_('كلمة المرور'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('أدخل كلمة المرور'),
        })
    )

    error_messages = {
        'invalid_login': _(
            'يرجى إدخال اسم مستخدم وكلمة مرور صحيحين. لاحظ أن كلا الحقلين قد يكون حساسًا للأحرف الكبيرة.'
        ),
        'inactive': _('هذا الحساب غير نشط.'),
    }


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_active'].label = _('نشط')

        ct = ContentType.objects.get_for_model(User)
        all_perms = Permission.objects.filter(content_type=ct, codename__in=ALL_PERM_CODENAMES)
        choices = [(p.codename, p.name) for p in all_perms]
        self.fields['permissions'] = forms.MultipleChoiceField(
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label=_('الصلاحيات'),
        )

    username = forms.CharField(
        label=_('اسم المستخدم'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('البريد الإلكتروني'),
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label=_('الاسم الأول'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('الاسم الأخير'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label=_('رقم الهاتف'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label=_('الدور'),
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'language_preference')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    first_name = forms.CharField(
        label=_('الاسم الأول'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('الاسم الأخير'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('البريد الإلكتروني'),
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label=_('رقم الهاتف'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    language_preference = forms.ChoiceField(
        label=_('اللغة'),
        choices=User.Language.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CustomPasswordChangeForm(BasePasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    old_password = forms.CharField(
        label=_('كلمة المرور الحالية'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label=_('كلمة المرور الجديدة'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=_('تأكيد كلمة المرور الجديدة'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
