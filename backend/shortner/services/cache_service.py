import redis
import json
import logging
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger('url_shortner')

class UrlCacheService:
    @staticmethod
    def get_cached_url(short_code):
        """
        Fetches cached URL data from Redis if it exists.
        """
        cached_data = cache.get(short_code)
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                logger.error(f'Error decoding cache for {short_code}')
                return None
        return None

    @staticmethod
    def cache_url_data(short_code, data, expiry_date=None):
        """
        Caches the URL data into Redis.
        expiry_date: Expiry date for the cached URL (from the database model).
        """
        redis_cache_expiry = None
        if expiry_date:
            now = timezone.now()
            remaining_seconds = (expiry_date - now).total_seconds()
            if remaining_seconds > 0:
                redis_cache_expiry = int(remaining_seconds)

        cache.set(short_code, json.dumps(data), timeout=redis_cache_expiry)

    @staticmethod
    def remove_cached_url(short_code):
        """
        Removes the cached URL data manually if needed.
        """
        cache.delete(short_code)