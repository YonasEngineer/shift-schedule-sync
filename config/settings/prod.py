from .base import *
import os


# # Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# # Read the .env file (you can point to specific paths dynamically)
# # This actually loads variables from the .env file into the system environment
# env.read_env(os.path.join(BASE_DIR, '.env.prod'))
# # Pull from .env.prod


# Explicitly tell it to use .env.prod
env_file = os.path.join(BASE_DIR, ".env.prod")

if os.path.exists(env_file):
    environ.Env.read_env(env_file)
else:
    print(f"Warning: {env_file} not found")


DEBUG = env('DEBUG')  # This will be False
SECRET_KEY = env('SECRET_KEY')
PORT = env.int('PORT')


# Strict production settings
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',

    }
}
