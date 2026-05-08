from django import forms

from apps.core.lookup_utils import set_lookup_choices

from .models import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierPayment


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['company_name', 'contact_person', 'phone', 'secondary_phone', 'email', 'address',
                  'supply_type', 'tax_number', 'payment_terms', 'current_balance', 'notes', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput)):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'payment_method', 'customer_payment_method')


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_delivery', 'status', 'subtotal', 'tax_percentage',
                  'tax_amount', 'shipping_cost', 'total', 'paid_amount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'expected_delivery': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput)):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'status', 'purchase_order_status')


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['material', 'quantity', 'unit_price', 'total', 'received_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = ['supplier', 'purchase_order', 'amount', 'payment_date', 'payment_method', 'reference', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput)):
                field.widget.attrs.setdefault('class', 'form-control')
