from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('<int:pk>/add-payment/', views.add_payment, name='add_payment'),
    path('<int:pk>/add-design/', views.add_design_file, name='add_design_file'),
    path('<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    path('<int:pk>/delivery-note/', views.add_delivery_note, name='add_delivery_note'),
    path('<int:pk>/print/', views.order_print, name='order_print'),
    path('<int:pk>/payment/<int:payment_pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('<int:pk>/timeline/', views.order_timeline, name='order_timeline'),
]
