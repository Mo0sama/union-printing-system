from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.lookup_utils import set_lookup_choices

from .models import Quote, QuoteItem


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [
            'customer', 'contact_person', 'valid_until', 'status',
            'discount_type', 'discount_value', 'tax_percentage',
            'notes', 'terms_conditions',
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'valid_until': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'discount_type': forms.Select(
                attrs={'class': 'form-control'}, choices=[('', '---')] + list(Quote.DiscountType.choices)
            ),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not hasattr(field.widget, 'attrs') or 'class' not in field.widget.attrs:
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'status', 'quote_status')
        set_lookup_choices(self, 'discount_type', 'discount_type')


class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ['description', 'quantity', 'unit', 'unit_price', 'discount_percent', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control unit-price-input', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(
                attrs={'class': 'form-control discount-input', 'step': '0.01'}
            ),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'unit', 'unit')


QuoteItemFormSet = forms.inlineformset_factory(
    Quote, QuoteItem, form=QuoteItemForm,
    extra=0, min_num=1, can_delete=True
)


class QuoteFilterForm(forms.Form):
    status = forms.ChoiceField(
        label=_('الحالة'), required=False,
        choices=[('', _('الكل'))] + list(Quote.Status.choices),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    customer = forms.CharField(
        label=_('العميل'), required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        label=_('من تاريخ'), required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        label=_('إلى تاريخ'), required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    search = forms.CharField(
        label=_('بحث'), required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _('رقم عرض السعر...')}
        )
    )
