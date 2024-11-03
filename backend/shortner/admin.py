from django.contrib import admin
from .models import shortnedURL

@admin.register(shortnedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_code', 'original_url', 'created_at', 'expires_at', 'is_active')
    search_fields = ('short_code', 'original_url', 'user__email')
    list_filter = ('is_active', 'expires_at')
    date_hierarchy = 'created_at'

# @admin.register(URLAnalytics)
# class URLAnalyticsAdmin(admin.ModelAdmin):
#     list_display = ('url', 'timestamp', 'ip_address', 'country', 'platform')
#     search_fields = ('url__short_code', 'ip_address', 'country', 'platform')
#     list_filter = ('timestamp', 'country', 'platform')
#     date_hierarchy = 'timestamp'
