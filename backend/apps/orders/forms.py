from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.lookup_utils import set_lookup_choices

from apps.inventory.models import Material

from .models import DeliveryNote, DesignFile, Order, OrderItem, OrderPayment


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer', 'quote', 'order_type', 'delivery_date',
            'status', 'priority', 'discount_type', 'discount_value',
            'tax_percentage', 'shipping_cost', 'payment_method',
            'notes', 'internal_notes', 'delivery_address',
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2'}),
            'quote': forms.Select(attrs={'class': 'form-control select2'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'discount_type': forms.Select(
                attrs={'class': 'form-control'},
                choices=[('', '---')] + list(Order.DiscountType.choices)
            ),
            'discount_value': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'tax_percentage': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'shipping_cost': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'payment_method': forms.Select(
                attrs={'class': 'form-control'},
                choices=[('', '---')] + list(Order.PaymentMethod.choices)
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'internal_notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'delivery_address': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not hasattr(field.widget, 'attrs') or 'class' not in field.widget.attrs:
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'order_type', 'order_type')
        set_lookup_choices(self, 'status', 'order_status')
        set_lookup_choices(self, 'priority', 'order_priority')
        set_lookup_choices(self, 'discount_type', 'discount_type')
        set_lookup_choices(self, 'payment_method', 'payment_method')


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            'item_type', 'description', 'design_file', 'quantity',
            'unit', 'unit_price', 'discount_percent',
            'production_notes', 'status', 'assigned_to', 'notes',
            'material',
        ]
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'design_file': forms.FileInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(
                attrs={'class': 'form-control unit-price-input', 'step': '0.01'}
            ),
            'discount_percent': forms.NumberInput(
                attrs={'class': 'form-control discount-input', 'step': '0.01'}
            ),
            'production_notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control select2'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'item_type', 'order_item_type')
        set_lookup_choices(self, 'unit', 'unit')
        set_lookup_choices(self, 'status', 'order_item_status')
        self.fields['material'].queryset = Material.objects.filter(is_active=True)
        self.fields['material'].required = False
        self.fields['material'].widget.attrs['data-placeholder'] = _('اختر خامة (اختياري)')


OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=0, min_num=1, can_delete=True
)


class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = OrderPayment
        fields = ['amount', 'payment_date', 'payment_method', 'reference', 'notes']
        widgets = {
            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'payment_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'payment_method', 'payment_method')


class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(
        label=_('الحالة'), required=False,
        choices=[('', _('الكل'))] + list(Order.Status.choices),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        label=_('الأولوية'), required=False,
        choices=[('', _('الكل'))] + list(Order.Priority.choices),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_status = forms.ChoiceField(
        label=_('حالة الدفع'), required=False,
        choices=[('', _('الكل'))] + list(Order.PaymentStatus.choices),
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
            attrs={'class': 'form-control', 'placeholder': _('رقم الطلب...')}
        )
    )


class DesignFileForm(forms.ModelForm):
    class Meta:
        model = DesignFile
        fields = ['file', 'version', 'notes']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control', 'multiple': True}),
            'version': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DeliveryNoteForm(forms.ModelForm):
    class Meta:
        model = DeliveryNote
        fields = ['delivered_by', 'received_by', 'delivery_date', 'items_delivered', 'status', 'notes']
        widgets = {
            'delivered_by': forms.TextInput(attrs={'class': 'form-control'}),
            'received_by': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'items_delivered': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'status', 'delivery_note_status')
