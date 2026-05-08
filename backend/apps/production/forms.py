from django import forms

from apps.core.lookup_utils import set_lookup_choices

from .models import Department, Machine, ProductionJob, ProductionStage, QualityCheck


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'name_ar', 'code', 'description', 'sort_order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name', 'machine_type', 'department', 'model', 'serial_number', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'machine_type', 'machine_type')
        set_lookup_choices(self, 'status', 'machine_status')


class ProductionJobForm(forms.ModelForm):
    class Meta:
        model = ProductionJob
        fields = ['order', 'order_item', 'department', 'machine', 'assigned_to', 'status', 'priority',
                  'quantity', 'completed_quantity', 'rejected_quantity', 'start_date', 'end_date',
                  'estimated_hours', 'actual_hours', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Textarea, forms.DateTimeInput)):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'status', 'production_job_status')
        set_lookup_choices(self, 'priority', 'order_priority')


class ProductionStageForm(forms.ModelForm):
    class Meta:
        model = ProductionStage
        fields = ['production_job', 'stage_name', 'stage_order', 'status', 'started_at', 'completed_at',
                  'completed_by', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'started_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'completed_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Textarea, forms.DateTimeInput)):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'status', 'production_stage_status')


class QualityCheckForm(forms.ModelForm):
    class Meta:
        model = QualityCheck
        fields = ['production_job', 'checked_by', 'result', 'defects', 'notes', 'attachments']
        widgets = {
            'defects': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'attachments': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.Textarea, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'result', 'quality_check_result')
