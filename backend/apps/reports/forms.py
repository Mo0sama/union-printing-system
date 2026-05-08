from django import forms


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label='من تاريخ',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError('تاريخ البداية يجب أن يكون قبل تاريخ النهاية')
        return cleaned_data


class ReportFilterForm(forms.Form):
    date_from = forms.DateField(
        label='من تاريخ', required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        label='إلى تاريخ', required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    department = forms.ChoiceField(
        label='القسم', required=False,
        choices=[
            ('', '--- الكل ---'),
            ('management', 'إدارة'),
            ('design', 'تصميم'),
            ('printing', 'طباعة'),
            ('finishing', 'تشطيب'),
            ('sales', 'مبيعات'),
            ('warehouse', 'مخزن'),
            ('delivery', 'توصيل'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        label='الحالة', required=False,
        choices=[
            ('', '--- الكل ---'),
            ('completed', 'مكتمل'),
            ('pending', 'قيد الانتظار'),
            ('cancelled', 'ملغي'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    group_by = forms.ChoiceField(
        label='تجميع حسب', required=False,
        choices=[
            ('day', 'يومي'),
            ('month', 'شهري'),
            ('year', 'سنوي'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
