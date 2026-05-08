from django.urls import path

from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.chart_of_accounts, name='chart_of_accounts'),
    path('journal/', views.journal_entry_list, name='journal_entry_list'),
    path('journal/create/', views.journal_entry_create, name='journal_entry_create'),
    path('journal/<int:pk>/', views.journal_entry_detail, name='journal_entry_detail'),
    path('reports/profit-loss/', views.profit_loss_report, name='profit_loss'),
    path('reports/balance-sheet/', views.balance_sheet_report, name='balance_sheet'),
    path('reports/sales/', views.sales_dashboard, name='sales_dashboard'),
]
