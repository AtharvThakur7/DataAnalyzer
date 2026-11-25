from django.contrib import admin
from .models import Dashboard, Chart

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']

@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ['title', 'chart_type', 'dashboard', 'dataset']
