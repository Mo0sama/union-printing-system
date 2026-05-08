from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User

from .models import CalculatorQuote


class ClientRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    first_name = forms.CharField(label=_('الاسم الأول'), required=True)
    last_name = forms.CharField(label=_('الاسم الأخير'), required=True)
    email = forms.EmailField(label=_('البريد الإلكتروني'), required=True)
    phone = forms.CharField(label=_('رقم الهاتف'), required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CLIENT
        user.is_staff = False
        if commit:
            user.save()
        return user


class QuoteSaveForm(forms.ModelForm):
    class Meta:
        model = CalculatorQuote
        fields = ['contact_name', 'contact_email', 'contact_phone', 'company', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
