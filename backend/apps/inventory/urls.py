from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
    path('movements/', views.stock_movement_list, name='stock_movement_list'),
    path('movements/create/', views.stock_movement_create, name='stock_movement_create'),
    path('adjustment/', views.stock_adjustment, name='stock_adjustment'),
    path('report/', views.inventory_report, name='inventory_report'),
    path('low-stock/', views.low_stock_report, name='low_stock_report'),
    path('valuations/', views.valuation_list, name='valuation_list'),
]
