from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path
from django.views.generic import RedirectView
from apps.accounts import views as accounts_views


def handler403(request, exception=None):
    return render(request, 'adminlte/403.html', status=403)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', RedirectView.as_view(url='/core/', permanent=False), name='home'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('accounts/', include('apps.accounts.urls')),
    path('customers/', include('apps.customers.urls')),
    path('quotes/', include('apps.quotes.urls')),
    path('orders/', include('apps.orders.urls')),
    path('production/', include('apps.production.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('employees/', include('apps.employees.urls')),
    path('pos/', include('apps.pos.urls')),
    path('reports/', include('apps.reports.urls')),
    path('calculator/', include('apps.calculator.urls')),
    path('core/', include('apps.core.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
