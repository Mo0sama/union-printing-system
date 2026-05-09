from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/bulk/', views.mark_bulk_attendance, name='mark_bulk_attendance'),

    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/create/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/approve/', views.leave_approve, name='leave_approve'),

    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/generate/', views.salary_generate, name='salary_generate'),
    path('salaries/<int:pk>/edit/', views.salary_edit, name='salary_edit'),
    path('salaries/<int:pk>/pay/', views.salary_pay, name='salary_pay'),

    path('advances/', views.advance_list, name='advance_list'),
    path('advances/create/', views.advance_create, name='advance_create'),

    path('reports/payroll/', views.payroll_report, name='payroll_report'),
]
