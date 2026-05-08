from django import forms
from apps.core.lookup_utils import set_lookup_choices
from .models import POSSession, POSSale


class POSSessionForm(forms.ModelForm):
    class Meta:
        model = POSSession
        fields = ['cashier', 'opening_balance', 'notes']
        widgets = {
            'cashier': forms.Select(attrs={'class': 'form-control select2'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class POSCloseForm(forms.ModelForm):
    class Meta:
        model = POSSession
        fields = ['closing_balance', 'notes']
        widgets = {
            'closing_balance': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01',
                'placeholder': 'أدخل الرصيد النقدي الفعلي',
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class POSSaleForm(forms.ModelForm):
    class Meta:
        model = POSSale
        fields = ['customer', 'payment_method', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'status', 'pos_sale_status')


class POSPaymentForm(forms.Form):
    amount_paid = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'step': '0.01',
            'id': 'amount-paid',
        })
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'نقدي'),
            ('card', 'بطاقة ائتمان'),
            ('bank_transfer', 'تحويل بنكي'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'payment-method'})
    )
