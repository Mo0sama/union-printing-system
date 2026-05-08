from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_dashboard, name='pos_dashboard'),
    path('session/open/', views.pos_session_open, name='pos_session_open'),
    path('session/<int:pk>/close/', views.pos_session_close, name='pos_session_close'),
    path('sessions/', views.pos_session_list, name='pos_session_list'),

    path('sale/new/', views.pos_sale_create, name='pos_sale_create'),
    path('sale/<int:pk>/', views.pos_sale_detail, name='pos_sale_detail'),
    path('sale/<int:pk>/refund/', views.pos_sale_refund, name='pos_sale_refund'),
    path('sales/', views.pos_sale_list, name='pos_sale_list'),

    path('receipt/<int:pk>/', views.pos_receipt, name='pos_receipt'),

    path('api/items/', views.pos_get_items, name='pos_get_items'),
]
