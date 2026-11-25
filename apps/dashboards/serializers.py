from rest_framework import serializers
from .models import Dashboard, Chart


class ChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chart
        fields = ['id', 'dashboard', 'dataset', 'title', 'chart_type', 'config', 'position', 'created_at']
        read_only_fields = ['id', 'created_at']


class DashboardSerializer(serializers.ModelSerializer):
    charts = ChartSerializer(many=True, read_only=True)
    chart_count = serializers.IntegerField(source='charts.count', read_only=True)

    class Meta:
        model = Dashboard
        fields = ['id', 'name', 'description', 'charts', 'chart_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
