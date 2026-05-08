from django.urls import path

from . import views

app_name = 'quotes'

urlpatterns = [
    path('', views.quote_list, name='quote_list'),
    path('create/', views.quote_create, name='quote_create'),
    path('<int:pk>/', views.quote_detail, name='quote_detail'),
    path('<int:pk>/edit/', views.quote_edit, name='quote_edit'),
    path('<int:pk>/delete/', views.quote_delete, name='quote_delete'),
    path('<int:pk>/convert/', views.quote_convert_to_order, name='quote_convert_to_order'),
    path('<int:pk>/print/', views.quote_print_pdf, name='quote_print_pdf'),
    path('<int:pk>/send-email/', views.quote_send_email, name='quote_send_email'),
]
