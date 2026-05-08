from django import forms
from apps.core.lookup_utils import set_lookup_choices
from .models import Employee, Attendance, EmployeeLeave, EmployeeSalary, EmployeeAdvance


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'full_name', 'full_name_ar', 'phone', 'email', 'position',
            'department', 'hire_date', 'salary_type', 'base_salary',
            'commission_percentage', 'id_number', 'address',
            'emergency_contact', 'emergency_phone', 'bank_account',
            'notes', 'is_active', 'photo',
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'commission_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name_ar': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'salary_type': forms.Select(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not hasattr(field.widget, 'attrs') or not field.widget.attrs.get('class'):
                field.widget.attrs.setdefault('class', 'form-control')
        set_lookup_choices(self, 'department', 'employee_dept')
        set_lookup_choices(self, 'salary_type', 'employee_salary_type')


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in', 'check_out', 'status', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control select2'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'check_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'status', 'attendance_status')


class BulkAttendanceForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class LeaveForm(forms.ModelForm):
    class Meta:
        model = EmployeeLeave
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control select2'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_lookup_choices(self, 'leave_type', 'leave_type')


class SalaryForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields = ['employee', 'month', 'base_salary', 'bonuses', 'deductions',
                  'commission', 'overtime', 'net_salary', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control select2'}),
            'month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'bonuses': forms.NumberInput(attrs={'class': 'form-control'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control'}),
            'commission': forms.NumberInput(attrs={'class': 'form-control'}),
            'overtime': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AdvanceForm(forms.ModelForm):
    class Meta:
        model = EmployeeAdvance
        fields = ['employee', 'amount', 'date', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control select2'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
