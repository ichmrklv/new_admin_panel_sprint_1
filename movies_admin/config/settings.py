from pathlib import Path
import os
from split_settings.tools import include
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"] 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = []

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

include(
    'components/database.py',
    'components/apps.py',
    'components/middleware.py',
    'components/templates.py',
    'components/auth.py',
    'components/internationalization.py',
) 

INTERNAL_IPS = [
    '127.0.0.1',
]
