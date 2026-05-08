from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),

    path('sales/', views.sales_report, name='sales_report'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('expenses/', views.expenses_report, name='expenses_report'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),

    path('customers/', views.customer_report, name='customer_report'),
    path('production/', views.production_report, name='production_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('employees/', views.employee_report, name='employee_report'),
    path('tax/', views.tax_report, name='tax_report'),

    path('export/', views.export_report_excel, name='export_report_excel'),
    path('print/', views.print_report, name='print_report'),
]
