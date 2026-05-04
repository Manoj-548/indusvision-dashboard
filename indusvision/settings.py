import os
from pathlib import Path
from dotenv import load_dotenv

# =========================================================
# BASE SETUP
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# =========================================================
# CORE SETTINGS
# =========================================================
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-key-change-in-production"
)

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

# IMPORTANT FIX
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")

# =========================================================
# SECURITY IMPROVEMENTS
# =========================================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
USE_X_FORWARDED_HOST = True

# HTTPS/SSL SETTINGS
# For production, set DEBUG=False and use proper SSL certificate
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SSL Certificate paths (for production HTTPS)
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", BASE_DIR / "dashboard.crt")
SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", BASE_DIR / "dashboard.key")

# =========================================================
# APPLICATIONS
# =========================================================
INSTALLED_APPS = [
"django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",
    "django_celery_beat",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    "dashboard",
    "api",
"annotation_app",
    "rag_engine",
    "ai_core",
    "workspace_manager",
    "yolo_integration",
]

# =========================================================
# AUTH / ALLAUTH
# =========================================================
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_URL = "/login/"

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

# =========================================================
# MIDDLEWARE
# =========================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "project_core.urls"

# =========================================================
# TEMPLATES
# =========================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project_core.wsgi.application"

# =========================================================
# DATABASE CONFIG
# =========================================================
USE_POSTGRES = os.getenv("USE_POSTGRES", "False").lower() == "true"

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
"NAME": os.getenv("POSTGRES_DB", "project_db"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 300,
            "OPTIONS": {
                "connect_timeout": 5,
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {
                "timeout": 30,
            },
        }
    }

# =========================================================
# INTERNATIONALIZATION
# =========================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC FILES
# =========================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# =========================================================
# MEDIA FILES (Nexify uploads / augmented images)
# =========================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================================
# CORS / API
# =========================================================
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny"
    ],
}

# =========================================================
# CELERY / REDIS
# =========================================================
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0"
)

CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0"
)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXPIRES = 3600

ENABLE_PERIODIC_TASKS = os.getenv(
    "ENABLE_PERIODIC_TASKS",
    "False"
).lower() == "true"

CELERY_BEAT_SCHEDULE = {}

if ENABLE_PERIODIC_TASKS:
    CELERY_BEAT_SCHEDULE = {
        "sync-source-files": {
            "task": "dashboard.tasks.celery_sync_source_files",
            "schedule": 300.0,
        },
        "consolidate-knowledge": {
            "task": "dashboard.tasks.celery_consolidate_knowledge_task",
            "schedule": 300.0,
        },
    }

# =========================================================
# TESTS
# =========================================================
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TESTS_DIR = BASE_DIR / 'tests'

# =========================================================
# PERFORMANCE / ML SAFETY
# =========================================================
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# =========================================================
# SQLITE WAL MODE (OPTIONAL BOOST)
# =========================================================
if not USE_POSTGRES:
    try:
        import sqlite3
        conn = sqlite3.connect(BASE_DIR / "db.sqlite3")
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.close()
    except Exception as e:
        print("SQLite WAL setup skipped:", e)

# =========================================================
# LOGGING (IMPROVED)
# =========================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple" if DEBUG else "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs/django.log",
            "maxBytes": 1024*1024*5,  # 5MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"] if not DEBUG else ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "dashboard": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

