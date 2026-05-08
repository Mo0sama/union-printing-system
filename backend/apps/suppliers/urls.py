from django.urls import path

from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    path('<int:pk>/payments/add/', views.add_supplier_payment, name='add_supplier_payment'),
    path('<int:pk>/ledger/', views.supplier_ledger, name='supplier_ledger'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/receive/', views.purchase_order_receive, name='purchase_order_receive'),
]
