import pandas as pd
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import logging

from .models import Dataset
from .serializers import DatasetSerializer, DatasetUploadSerializer
from .services import (
    read_file_to_dataframe, extract_column_metadata,
    compute_dataset_stats, clean_dataframe, get_data_page,
)
from apps.core.cache import (
    get_cached_stats, set_cached_stats,
    get_cached_chart_data, set_cached_chart_data,
    invalidate_dataset_cache,
)

logger = logging.getLogger(__name__)

_df_cache: dict[int, 'pd.DataFrame'] = {}


def _get_df(dataset: Dataset):
    if dataset.id not in _df_cache:
        _df_cache[dataset.id] = read_file_to_dataframe(
            dataset.file.path, dataset.file_type
        )
    return _df_cache[dataset.id]


def _compute_single_chart(df, spec):
    x_col = spec.get('x_column', '')
    y_col = spec.get('y_column') or ''
    agg = spec.get('aggregation', 'mean')
    chart_type = spec.get('chart_type', 'bar')

    if not x_col or x_col not in df.columns:
        return None
    if y_col and y_col not in df.columns:
        y_col = ''

    use_value_counts = (
        not y_col
        or agg in (None, '', 'none')
    )

    if use_value_counts:
        vc = df[x_col].value_counts().head(30)
        x_data = vc.index.astype(str).tolist()
        y_data = vc.values.tolist()
        y_label = 'Count'
    elif agg == 'count':
        grouped = df.groupby(x_col, observed=True).size().reset_index(name='count')
        x_data = grouped[x_col].astype(str).tolist()
        y_data = grouped['count'].tolist()
        y_label = 'Count'
    elif pd.api.types.is_numeric_dtype(df[y_col]):
        grouped = df.groupby(x_col, observed=True)[y_col].agg(agg).reset_index()
        x_data = grouped[x_col].astype(str).tolist()
        y_data = grouped[y_col].tolist()
        y_label = y_col
    else:
        grouped = df.groupby(x_col, observed=True).size().reset_index(name='count')
        x_data = grouped[x_col].astype(str).tolist()
        y_data = grouped['count'].tolist()
        y_label = 'Count'

    y_data = [
        0 if (isinstance(v, float) and (v != v or abs(v) == float('inf')))
        else round(v, 4) if isinstance(v, float) else v
        for v in y_data
    ]

    return {
        'chart_type': chart_type,
        'title': spec.get('title', ''),
        'x_data': x_data,
        'y_data': y_data,
        'x_label': x_col,
        'y_label': y_label,
    }


class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = DatasetUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        ext = file.name.rsplit('.', 1)[-1].lower()
        if ext not in ('csv', 'xlsx', 'xls'):
            return Response(
                {'error': 'Only CSV and Excel files are supported.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name = serializer.validated_data.get('name') or file.name.rsplit('.', 1)[0]

        dataset = Dataset.objects.create(
            user=request.user,
            name=name,
            original_filename=file.name,
            file=file,
            file_type=ext,
            size_bytes=file.size,
        )

        try:
            df = read_file_to_dataframe(dataset.file.path, ext)
            dataset.row_count = len(df)
            dataset.col_count = len(df.columns)
            dataset.columns_meta = extract_column_metadata(df)
            dataset.save()
            _df_cache[dataset.id] = df
        except Exception as e:
            logger.error(f"Failed to process dataset {dataset.id}: {e}")
            dataset.delete()
            return Response(
                {'error': f'Failed to read file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        dataset = self.get_object()
        _df_cache.pop(dataset.id, None)
        invalidate_dataset_cache(dataset.id)
        dataset.file.delete(save=False)
        dataset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        dataset = self.get_object()
        df = _get_df(dataset)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        df_clean = df.where(df.notna(), None)
        result = get_data_page(df_clean, page, page_size)
        return Response(result)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        dataset = self.get_object()
        cached = get_cached_stats(dataset.id)
        if cached:
            return Response(cached)
        df = _get_df(dataset)
        result = compute_dataset_stats(df)
        set_cached_stats(dataset.id, result)
        return Response(result)

    @action(detail=True, methods=['post'])
    def clean(self, request, pk=None):
        dataset = self.get_object()
        df = _get_df(dataset)
        cleaned_df, report = clean_dataframe(df.copy())
        _df_cache[dataset.id] = cleaned_df
        dataset.row_count = len(cleaned_df)
        dataset.col_count = len(cleaned_df.columns)
        dataset.columns_meta = extract_column_metadata(cleaned_df)
        dataset.is_cleaned = True
        dataset.save()
        invalidate_dataset_cache(dataset.id)
        return Response({'report': report, 'dataset': DatasetSerializer(dataset).data})

    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None):
        dataset = self.get_object()
        return Response(dataset.columns_meta)

    @action(detail=True, methods=['post'])
    def chart_data(self, request, pk=None):
        dataset = self.get_object()
        x_col = request.data.get('x_column')
        if not x_col:
            return Response({'error': 'x_column is required'}, status=400)

        cache_params = {
            'ct': request.data.get('chart_type', 'bar'),
            'x': x_col,
            'y': request.data.get('y_column'),
            'a': request.data.get('aggregation', 'mean'),
        }
        cached = get_cached_chart_data(dataset.id, cache_params)
        if cached:
            return Response(cached)

        df = _get_df(dataset)
        try:
            result = _compute_single_chart(df, request.data)
            if result is None:
                return Response({'error': f'Column "{x_col}" not found'}, status=400)
            set_cached_chart_data(dataset.id, cache_params, result)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def batch_charts(self, request, pk=None):
        dataset = self.get_object()
        specs = request.data.get('charts', [])[:10]
        df = _get_df(dataset)
        results = []
        for spec in specs:
            try:
                results.append(_compute_single_chart(df, spec))
            except Exception:
                results.append(None)
        return Response({'charts': results})
