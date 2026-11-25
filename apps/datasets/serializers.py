from rest_framework import serializers
from .models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'original_filename', 'file_type',
            'row_count', 'col_count', 'columns_meta', 'size_bytes',
            'is_cleaned', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'original_filename', 'file_type', 'row_count',
            'col_count', 'columns_meta', 'size_bytes', 'created_at', 'updated_at',
        ]


class DatasetUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)
