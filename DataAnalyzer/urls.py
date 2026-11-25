from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.core.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/datasets/', include('apps.datasets.urls')),
    path('api/ai/', include('apps.ai_insights.urls')),
    path('health/', health_check, name='health'),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('app/', TemplateView.as_view(template_name='app.html'), name='app'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
