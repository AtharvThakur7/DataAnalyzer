from django.db import models
from django.contrib.auth.models import User
from apps.datasets.models import Dataset


class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        return self.name


class Chart(models.Model):
    CHART_TYPES = [
        ('bar', 'Bar'), ('line', 'Line'), ('pie', 'Pie'),
        ('scatter', 'Scatter'), ('area', 'Area'), ('heatmap', 'Heatmap'),
        ('histogram', 'Histogram'), ('donut', 'Donut'), ('radar', 'Radar'),
    ]

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='charts')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='charts')
    title = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    config = models.JSONField(default=dict)
    position = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.chart_type})"
