from django import forms

from apps.core.lookup_utils import set_lookup_choices

from .models import Category, Material, StockMovement


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'name_ar', 'parent', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'name_ar', 'category', 'unit', 'purchase_price', 'selling_price',
                  'current_stock', 'minimum_stock', 'location', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'unit', 'unit')


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['material', 'batch', 'movement_type', 'quantity', 'unit_price', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'movement_type', 'stock_movement_type')


class StockTransferForm(forms.Form):
    material = forms.ModelChoiceField(queryset=Material.objects.filter(is_active=True), label='الخامة')
    quantity = forms.DecimalField(max_digits=12, decimal_places=2, label='الكمية')
    from_location = forms.CharField(max_length=200, label='من موقع')
    to_location = forms.CharField(max_length=200, label='إلى موقع')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False, label='ملاحظات')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
