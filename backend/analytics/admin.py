from django.contrib import admin
from .models import URLAnalytics

@admin.register(URLAnalytics)
class URLAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('url', 'timestamp', 'ip_address', 'user_agent', 'referrer', 'country', 'platform', 'device_type', 'access_count')
    list_filter = ('timestamp', 'country', 'platform', 'device_type')
    search_fields = ('url__short_code', 'ip_address', 'user_agent', 'country', 'platform')
    readonly_fields = ('url', 'timestamp', 'ip_address', 'user_agent', 'referrer', 'country', 'platform', 'device_type', 'access_count')
    ordering = ('-timestamp',)

    def get_queryset(self, request):
        # Customize queryset for the admin to include related URL info
        qs = super().get_queryset(request)
        return qs.select_related('url')
