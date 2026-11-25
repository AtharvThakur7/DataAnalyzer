import hashlib
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

STATS_TTL = 600
METADATA_TTL = 1800


def _cache_key(prefix: str, dataset_id: int, extra: str = '') -> str:
    return f'qi:{prefix}:{dataset_id}:{extra}' if extra else f'qi:{prefix}:{dataset_id}'


def get_cached_stats(dataset_id: int):
    return cache.get(_cache_key('stats', dataset_id))


def set_cached_stats(dataset_id: int, stats: dict):
    cache.set(_cache_key('stats', dataset_id), stats, STATS_TTL)


def get_cached_chart_data(dataset_id: int, params: dict):
    param_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()[:12]
    return cache.get(_cache_key('chart', dataset_id, param_hash))


def set_cached_chart_data(dataset_id: int, params: dict, data: dict):
    param_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()[:12]
    cache.set(_cache_key('chart', dataset_id, param_hash), data, STATS_TTL)


def invalidate_dataset_cache(dataset_id: int):
    cache.delete(_cache_key('stats', dataset_id))
    try:
        cache.delete_pattern(f'qi:chart:{dataset_id}:*')
    except (AttributeError, NotImplementedError):
        pass
