# Generated by Django 5.1 on 2024-09-22 19:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='shortnedURL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.URLField(max_length=2048)),
                ('short_code', models.CharField(db_index=True, max_length=10, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='URLAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.CharField(max_length=512)),
                ('referrer', models.CharField(blank=True, max_length=2048, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('platform', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='shortner.shortnedurl')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='shortnedurl',
            index=models.Index(fields=['short_code'], name='shortner_sh_short_c_70c2aa_idx'),
        ),
        migrations.AddIndex(
            model_name='shortnedurl',
            index=models.Index(fields=['expires_at'], name='shortner_sh_expires_ad1ca9_idx'),
        ),
        migrations.AddIndex(
            model_name='shortnedurl',
            index=models.Index(fields=['user', 'created_at'], name='shortner_sh_user_id_a93a6f_idx'),
        ),
        migrations.AddIndex(
            model_name='urlanalytics',
            index=models.Index(fields=['url'], name='shortner_ur_url_id_4aeaea_idx'),
        ),
        migrations.AddIndex(
            model_name='urlanalytics',
            index=models.Index(fields=['timestamp'], name='shortner_ur_timesta_f7203f_idx'),
        ),
    ]