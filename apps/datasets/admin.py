from django.contrib import admin
from .models import Dataset

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'file_type', 'row_count', 'col_count', 'created_at']
    list_filter = ['file_type', 'is_cleaned']
    search_fields = ['name', 'user__username']
