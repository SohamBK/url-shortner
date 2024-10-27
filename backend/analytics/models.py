from django.db import models
from shortner.models import shortnedURL

class URLAnalytics(models.Model):
    url = models.ForeignKey(shortnedURL, on_delete=models.CASCADE, related_name='analytics')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=512)
    referrer = models.CharField(max_length=2048, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    access_count = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f'Analytics for {self.url.short_code} at {self.timestamp}'