from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    FILE_TYPES = [('csv', 'CSV'), ('xlsx', 'Excel'), ('xls', 'Excel (Legacy)')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/%Y/%m/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    row_count = models.IntegerField(default=0)
    col_count = models.IntegerField(default=0)
    columns_meta = models.JSONField(default=dict, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    is_cleaned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['file_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.row_count}x{self.col_count})"
