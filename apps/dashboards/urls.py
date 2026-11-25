from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('dashboards', views.DashboardViewSet, basename='dashboard')
router.register('charts', views.ChartViewSet, basename='chart')

urlpatterns = [
    path('', include(router.urls)),
]
