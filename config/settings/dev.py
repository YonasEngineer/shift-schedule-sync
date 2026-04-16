from .base import *
import os


# Adjust BASE_DIR to point to your project root
# (Three .parent calls if you are in config/settings/dev.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": True
}
# # Read the .env file (you can point to specific paths dynamically)
# # This actually loads variables from the .env file into the system environment
# env.read_env(os.path.join(BASE_DIR, '.env.dev'))

# Explicitly tell it to use .env.dev
env_file = os.path.join(BASE_DIR, ".env.dev")

if os.path.exists(env_file):
    environ.Env.read_env(env_file)
else:
    print(f"Warning: {env_file} not found")

# Pull from .env.dev
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
PORT = env.int('PORT')

# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]  # for development only
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# VERY IMPORTANT for cookies
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]


SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False  # True in production (HTTPS)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shift_schedule',
        'USER': 'shiftmanager',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
