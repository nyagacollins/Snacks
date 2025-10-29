from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.generic import RedirectView

def favicon_view(request):
    return HttpResponse(status=204)  # No content

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:login')),
    path('favicon.ico', favicon_view, name='favicon'),
    path('accounts/', include('apps.accounts.urls')),
    path('products/', include('apps.products.urls')),
    path('payments/', include('apps.payments.urls')),
    path('reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)