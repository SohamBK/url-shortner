from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()
# URL Shortener Model
class shortnedURL(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="urls")
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.short_code} -> {self.original_url}'

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at