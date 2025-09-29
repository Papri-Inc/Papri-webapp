# backend/applaude_api/settings/production.py
from .base import *
import os
import dj_database_url
import boto3
import json

# ==============================================================================
# AWS SECRETS MANAGER CONFIGURATION
# ==============================================================================
# This block fetches secrets from AWS Secrets Manager and loads them into the
# environment. This avoids the 4096-byte limit for environment variables and
# is more secure.

secrets_arn = os.environ.get('SECRETS_MANAGER_ARN')
if secrets_arn:
    session = boto3.session.Session()
    # Ensure you specify the correct region where your secret is stored.
    client = session.client(service_name='secretsmanager', region_name='us-east-1') 
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secrets_arn)
        secret = json.loads(get_secret_value_response['SecretString'])
        
        # Set the fetched secrets as environment variables so the rest of the settings file can use them
        for key, value in secret.items():
            os.environ[key] = str(value)
    except Exception as e:
        # In case of an error, it's better to raise it to prevent the app from running with missing secrets.
        raise Exception(f"Failed to fetch secrets from AWS Secrets Manager: {e}")

# ==============================================================================
# CORE DJANGO SETTINGS
# ==============================================================================

# DEBUG should always be False in production.
DEBUG = False

# The SECRET_KEY is now fetched from Secrets Manager via the code block above.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Configure allowed hosts. Fetched from environment variable set in Elastic Beanstalk.
# Example Value: "papri.us-east-1.elasticbeanstalk.com,.elasticbeanstalk.com"
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ==============================================================================
# CORS (Cross-Origin Resource Sharing) CONFIGURATION
# ==============================================================================
# This allows your Vercel frontend to communicate with your backend API.

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# Ensure CORS applies to all API endpoints
CORS_URLS_REGEX = r'^/api/.*$'

# ==============================================================================
# PRODUCTION SECURITY SETTINGS
# ==============================================================================
# These settings enhance your application's security in a production environment.

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================
# The DATABASE_URL is now fetched from Secrets Manager.

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ==============================================================================
# REDIS & CELERY CONFIGURATION
# ==============================================================================
# The REDIS_URL is fetched from the Elastic Beanstalk environment variables.

REDIS_URL = os.environ.get("REDIS_URL")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
RATELIMIT_USE_CACHE = 'default'


# ==============================================================================
# STATIC & MEDIA FILES (AWS S3) CONFIGURATION
# ==============================================================================
# This configures Django to store and serve static and media files from S3.

# Use IAM Role for credentials, so AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are not needed.
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1') # Default to us-east-1 if not set
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# Static files location
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files location
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
# MEDIA_ROOT is not needed when using S3
