from django.urls import path

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('quick-add/', views.quick_add_customer, name='quick_add_customer'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('<int:pk>/interaction/add/', views.add_interaction, name='add_interaction'),
    path('<int:pk>/payment/add/', views.add_payment, name='add_payment'),
    path('<int:pk>/statement/', views.customer_statement, name='customer_statement'),
    path('export/', views.customer_export, name='customer_export'),
]
