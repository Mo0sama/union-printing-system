from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('activity-log/', views.activity_log_list, name='activity_log'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/advanced/', views.advanced_settings, name='advanced_settings'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('clear-notifications/', views.clear_notifications, name='clear_notifications'),
]
