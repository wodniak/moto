"""
    Views are mapped to urls here
"""

from django.urls import path
from .views import MotoView
from . import views

urlpatterns = [
    path('', MotoView.as_view(), name='index'),
    path(r'^barplot.png$', views.show_graphs, name='show_graphs'),
    path('<int:idx>/', views.detail_moto, name='detail_moto')
]
