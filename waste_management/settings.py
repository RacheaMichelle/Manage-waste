"""
Django settings for waste_management project.
"""

from pathlib import Path
import os
import dj_database_url
from django.core.management.utils import get_random_secret_key

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'i(s37lgb*j3pwnfz9z9a8z$b3j1-5sk0!1dkv^-_-#cr02mo)q')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Render automatically sets RENDER_EXTERNAL_HOSTNAME
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '.onrender.com']
else:
    ALLOWED_HOSTS = []

# Add your existing allowed hosts
ALLOWED_HOSTS.extend([
    'localhost',
    '127.0.0.1',
    'cleanuganda.com',
    'www.cleanuganda.com',
    '.vercel.app',  # Keep for reference
    '.now.sh',      # Keep for reference
])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    
    # Custom apps
    'users',
    'waste',
    'matching',
    'analytics',
    'education',
    'educ',
    'report',
    'chatbot',
    
    # Third-party apps
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'waste_management.urls'

# Security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rachealnannozi77@gmail.com'
EMAIL_HOST_PASSWORD = 'iaegpsdmhisbhwfp'
DEFAULT_FROM_EMAIL = 'rachealnannozi77@gmail.com'

# Use database sessions
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Template configuration - FIXED
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'waste_management.context_processors.seo_context',
                'users.context_processors.quick_access_status', 
            ],
        },
    },
]

# Application performance optimizations - FIXED TEMPLATE CACHING
if not DEBUG:
    # Template caching in production - CORRECTED VERSION
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

WSGI_APPLICATION = 'waste_management.wsgi.application'

# DATABASE CONFIGURATION FOR NEON.POSTGRESQL + RENDER - FIXED
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_qw4cSXLRezU0@ep-restless-lake-abe1tpdg-pooler.eu-west-2.aws.neon.tech/neondb')

# Always use Neon PostgreSQL on Render
if DATABASE_URL:
    # Clean the database URL for Neon
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Remove any query parameters that might cause issues
    if '?' in DATABASE_URL:
        base_url = DATABASE_URL.split('?')[0]
        DATABASE_URL = base_url
    
    # Use dj-database-url for robust configuration
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
    
    # Ensure PostgreSQL engine is used and add connection optimizations
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 30,
    }
    
else:
    # Fallback for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ensure static directories exist
try:
    os.makedirs(BASE_DIR / 'static', exist_ok=True)
    os.makedirs(BASE_DIR / 'staticfiles', exist_ok=True)
except OSError:
    pass

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Ensure media directory exists
try:
    os.makedirs(MEDIA_ROOT, exist_ok=True)
except OSError:
    pass

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID for Django sites framework
SITE_ID = 1

# SEO Settings
SITE_NAME = "Clean Uganda"
SITE_DESCRIPTION = "Uganda's leading waste management and recycling platform"
META_KEYWORDS = "Clean Uganda, waste management Uganda, recycling Kampala, clean environment Uganda"

# Authentication URLs
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'waste_management': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Cache configuration (using database cache as fallback)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Custom settings
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Render-specific optimizations
IS_RENDER = os.environ.get('RENDER') == 'true'

if IS_RENDER:
    print("Running on Render environment")
    
    # Render-specific optimizations
    DATABASES['default']['CONN_MAX_AGE'] = 60
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
    
    # Ensure static files are served efficiently
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_MANIFEST_STRICT = False
    WHITENOISE_ALLOW_ALL_ORIGINS = True

# Health check configuration for Render
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,     # in MB
}

# Cloudinary configuration (if using)
if os.environ.get('CLOUDINARY_URL'):
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

# Print deployment info for debugging
print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"DATABASE ENGINE: {DATABASES['default'].get('ENGINE', 'Unknown')}")
print(f"DATABASE NAME: {DATABASES['default'].get('NAME', 'Unknown')}")
print(f"RENDER: {IS_RENDER}")
