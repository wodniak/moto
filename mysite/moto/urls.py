"""
    Views are mapped to urls here
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views.start import MotoView
from .views.detail import DetailView


urlpatterns = [
    path('', MotoView.as_view(), name='index'),
    path('detail/', DetailView.as_view(), name='detail')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
