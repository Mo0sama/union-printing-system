from django.urls import path

from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.calculator_home, name='calculator_home'),
    path('printing/', views.printing_calculator, name='printing_calculator'),
    path('giveaways/', views.giveaway_calculator, name='giveaway_calculator'),
    path('api/calculate/', views.api_calculate, name='api_calculate'),
    path('api/save-quote/', views.save_quote, name='save_quote'),
    path('register/', views.client_register, name='client_register'),
    path('my-quotes/', views.my_quotes, name='my_quotes'),
    path('my-quotes/<int:pk>/', views.my_quote_detail, name='my_quote_detail'),
]
