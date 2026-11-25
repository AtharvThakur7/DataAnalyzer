from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as http_status
from django.shortcuts import get_object_or_404

from apps.datasets.models import Dataset
from apps.datasets.views import _get_df, _compute_single_chart
from apps.datasets.services import compute_dataset_stats
from . import services


def _get_dataset_context(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    df = _get_df(dataset)
    stats = compute_dataset_stats(df)
    sample = df.head(5).to_dict('records')
    return dataset, df, stats, sample


def _resolve_chart_data(df, charts):
    resolved = []
    for spec in (charts or [])[:8]:
        try:
            data = _compute_single_chart(df, spec)
            if data:
                data['title'] = spec.get('title', data.get('title', ''))
                data['reason'] = spec.get('reason', '')
                resolved.append(data)
        except Exception:
            pass
    return resolved


@api_view(['POST'])
def ask_question(request):
    dataset_id = request.data.get('dataset_id')
    question = request.data.get('question', '').strip()

    if not dataset_id or not question:
        return Response(
            {'error': 'dataset_id and question are required'},
            status=http_status.HTTP_400_BAD_REQUEST,
        )

    dataset, df, stats, sample = _get_dataset_context(request, dataset_id)

    try:
        result = services.ask_question(
            question, dataset.columns_meta, stats, sample, df=df,
        )
        chart_data = _resolve_chart_data(df, result['charts'])
        return Response({
            'answer': result['text'],
            'charts': result['charts'],
            'chart_data': chart_data,
            'computed': result.get('computed'),
            'dataset_id': dataset_id,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_insights(request):
    dataset_id = request.data.get('dataset_id')
    if not dataset_id:
        return Response({'error': 'dataset_id is required'}, status=http_status.HTTP_400_BAD_REQUEST)

    dataset, df, stats, sample = _get_dataset_context(request, dataset_id)

    try:
        result = services.generate_insights(
            dataset.columns_meta, stats, sample, df=df,
        )
        chart_data = _resolve_chart_data(df, result['charts'])
        return Response({
            'insights': result['text'],
            'charts': result['charts'],
            'chart_data': chart_data,
            'dataset_id': dataset_id,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def suggest_charts(request):
    dataset_id = request.data.get('dataset_id')
    if not dataset_id:
        return Response({'error': 'dataset_id is required'}, status=http_status.HTTP_400_BAD_REQUEST)

    dataset, df, stats, sample = _get_dataset_context(request, dataset_id)

    try:
        suggestions = services.suggest_charts(dataset.columns_meta, stats)
        chart_data = _resolve_chart_data(df, suggestions)
        return Response({
            'suggestions': suggestions,
            'chart_data': chart_data,
            'dataset_id': dataset_id,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_report(request):
    dataset_id = request.data.get('dataset_id')
    if not dataset_id:
        return Response({'error': 'dataset_id is required'}, status=http_status.HTTP_400_BAD_REQUEST)

    dataset, df, stats, sample = _get_dataset_context(request, dataset_id)

    try:
        report = services.generate_report_content(
            dataset.columns_meta, stats, sample, df=df,
        )
        chart_data = _resolve_chart_data(df, report['charts'])
        return Response({
            'report': report['text'],
            'charts': report['charts'],
            'chart_data': chart_data,
            'dataset_id': dataset_id,
            'dataset_name': dataset.name,
            'stats': stats,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
