from .base import *
import os


# Adjust BASE_DIR to point to your project root
# (Three .parent calls if you are in config/settings/dev.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


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


ALLOWED_HOSTS = ['localhost', '127.0.0.1']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}
