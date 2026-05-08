from django.urls import path

from . import views

app_name = 'production'

urlpatterns = [
    path('', views.production_dashboard, name='production_dashboard'),
    path('jobs/', views.production_job_list, name='production_job_list'),
    path('jobs/create/', views.production_job_create, name='production_job_create'),
    path('jobs/<int:pk>/', views.production_job_detail, name='production_job_detail'),
    path('jobs/<int:pk>/edit/', views.production_job_edit, name='production_job_edit'),
    path('jobs/<int:pk>/status/', views.update_job_status, name='update_job_status'),
    path('jobs/<int:pk>/assign/', views.assign_job, name='assign_job'),
    path('jobs/<int:job_pk>/quality-check/', views.quality_check_create, name='quality_check_create'),
    path('machines/', views.machine_list, name='machine_list'),
    path('machines/create/', views.machine_create, name='machine_create'),
    path('machines/<int:pk>/edit/', views.machine_edit, name='machine_edit'),
    path('departments/', views.department_list, name='department_list'),
    path('report/', views.production_report, name='production_report'),
    path('quick-add/department/', views.quick_add_department, name='quick_add_department'),
    path('quick-add/machine/', views.quick_add_machine, name='quick_add_machine'),
    path('quick-add/employee/', views.quick_add_employee, name='quick_add_employee'),
]
