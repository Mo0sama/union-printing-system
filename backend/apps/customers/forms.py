from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.lookup_utils import set_lookup_choices

from .models import Customer, CustomerContact, CustomerInteraction, CustomerPayment


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = (
            'customer_type', 'name', 'company_name', 'contact_person',
            'phone', 'secondary_phone', 'email', 'address', 'city',
            'tax_number', 'credit_limit', 'notes', 'is_active',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('اسم العميل')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'customer_type', 'customer_type')

        self.fields['name'].required = False
        self.fields['company_name'].required = False
        self.fields['contact_person'].required = False

    customer_type = forms.ChoiceField(
        label=_('نوع العميل'),
        choices=Customer.CustomerType.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        label=_('الاسم'), required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': _('اسم العميل')
        })
    )
    company_name = forms.CharField(
        label=_('اسم الشركة'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    contact_person = forms.CharField(
        label=_('الشخص المسؤول'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label=_('رقم الهاتف'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    secondary_phone = forms.CharField(
        label=_('هاتف آخر'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('البريد الإلكتروني'), required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        label=_('العنوان'), required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    city = forms.CharField(
        label=_('المدينة'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tax_number = forms.CharField(
        label=_('الرقم الضريبي'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    credit_limit = forms.DecimalField(
        label=_('الحد الائتماني'), required=False, initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label=_('ملاحظات'), required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    is_active = forms.BooleanField(
        label=_('نشط'), required=False, initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        customer_type = cleaned_data.get('customer_type')

        if customer_type == 'individual':
            name = cleaned_data.get('name', '').strip()
            if not name:
                self.add_error('name', _('الاسم مطلوب للأفراد'))
            cleaned_data['company_name'] = ''
            cleaned_data['contact_person'] = ''
        elif customer_type == 'company':
            company_name = cleaned_data.get('company_name', '').strip()
            if not company_name:
                self.add_error('company_name', _('اسم الشركة مطلوب'))
            if not cleaned_data.get('name', '').strip():
                cleaned_data['name'] = company_name

        return cleaned_data


class CustomerContactForm(forms.ModelForm):
    class Meta:
        model = CustomerContact
        fields = ('name', 'phone', 'email', 'position', 'is_primary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    name = forms.CharField(
        label=_('الاسم'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label=_('رقم الهاتف'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('البريد الإلكتروني'), required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    position = forms.CharField(
        label=_('المسمى الوظيفي'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_primary = forms.BooleanField(
        label=_('جهة اتصال رئيسية'), required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class CustomerInteractionForm(forms.ModelForm):
    class Meta:
        model = CustomerInteraction
        fields = ('interaction_type', 'summary', 'details')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'interaction_type', 'interaction_type')

    interaction_type = forms.ChoiceField(
        label=_('نوع التفاعل'),
        choices=CustomerInteraction.InteractionType.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    summary = forms.CharField(
        label=_('ملخص'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    details = forms.CharField(
        label=_('تفاصيل'), required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )


class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerPayment
        fields = ('amount', 'payment_date', 'payment_method', 'reference', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'payment_method', 'customer_payment_method')

    amount = forms.DecimalField(
        label=_('المبلغ'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    payment_date = forms.DateField(
        label=_('تاريخ الدفع'),
        widget=forms.DateInput(attrs={
            'class': 'form-control', 'type': 'date'
        })
    )
    payment_method = forms.ChoiceField(
        label=_('طريقة الدفع'),
        choices=CustomerPayment.PaymentMethod.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reference = forms.CharField(
        label=_('مرجع'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label=_('ملاحظات'), required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
