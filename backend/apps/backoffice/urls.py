from django.urls import path

from . import views

app_name = 'backoffice'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('labels/', views.label_list, name='label_list'),
    path('labels/<path:key>/edit/', views.label_edit, name='label_edit'),
    path('labels/<path:key>/reset/', views.label_reset, name='label_reset'),
    path('import/', views.import_labels, name='import_labels'),
]
