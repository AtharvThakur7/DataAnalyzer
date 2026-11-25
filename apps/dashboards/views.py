from rest_framework import viewsets
from .models import Dashboard, Chart
from .serializers import DashboardSerializer, ChartSerializer


class DashboardViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardSerializer

    def get_queryset(self):
        return Dashboard.objects.filter(user=self.request.user).prefetch_related('charts')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChartViewSet(viewsets.ModelViewSet):
    serializer_class = ChartSerializer

    def get_queryset(self):
        return Chart.objects.filter(dashboard__user=self.request.user)
