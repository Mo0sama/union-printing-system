import json

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include, path
from django.views.generic import RedirectView

from apps.accounts import views as accounts_views


def manifest_view(request):
    manifest = {
        "name": "Union for Printing Services",
        "short_name": "Union Printing",
        "description": "\u0645\u0643\u062a\u0628 \u0627\u0644\u0627\u062a\u062d\u0627\u062f \u0644\u0644\u0637\u0628\u0627\u0639\u0629 - Union for Digital Printing Services",
        "start_url": "/calculator/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#1a1a1a",
        "theme_color": "#e65100",
        "orientation": "portrait-primary",
        "lang": "ar",
        "dir": "rtl",
        "icons": [
            {
                "src": "/static/images/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "/static/images/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }
    return HttpResponse(
        json.dumps(manifest, ensure_ascii=False),
        content_type="application/manifest+json; charset=utf-8",
    )


def handler403(request, exception=None):
    return render(request, 'adminlte/403.html', status=403)


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('manifest.json', manifest_view, name='manifest'),
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
    path('accounting/', include('apps.accounting.urls')),
    path('core/', include('apps.core.urls')),
    path('backoffice/', include('apps.backoffice.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
