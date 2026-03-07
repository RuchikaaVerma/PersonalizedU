from pathlib import Path
from datetime import timedelta

# ── Base ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#fc5z#@h4ei=qz%u2+yzryl+cfn(eq16i=-jw6%(2#4-8%nsc2'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ── Apps ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'learning',
]


# ── Middleware (CorsMiddleware MUST be first) ─────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # ← must be #1
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ── URL & WSGI ────────────────────────────────────────
ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'


# ── Templates ─────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ── Database ──────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ── Password Validation ───────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Internationalisation ──────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True


# ── Static Files ──────────────────────────────────────
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── CORS ──────────────────────────────────────────────
# Allows the frontend (Live Server) and webhook to talk to Django
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',   # VS Code Live Server (frontend)
    'http://localhost:5500',   # alternate Live Server address
    'http://localhost:3000',   # Node.js webhook
    'http://127.0.0.1:3000',   # alternate webhook address
]

# Keep True during development — set False and use CORS_ALLOWED_ORIGINS in production
CORS_ALLOW_ALL_ORIGINS = True

# Allow Authorization header for JWT tokens sent from frontend
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ── Django REST Framework ─────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# ── Simple JWT ────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=6),    # stay logged in for 6 hours
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # refresh token valid 7 days
    'ROTATE_REFRESH_TOKENS':  True,                  # issue new refresh token on each refresh
    'BLACKLIST_AFTER_ROTATION': False,               # keep simple — no blacklist app needed
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ── Ollama (local AI) ─────────────────────────────────
OLLAMA_URL   = 'http://localhost:11434/v1/chat/completions'
OLLAMA_MODEL = 'llama3.2'