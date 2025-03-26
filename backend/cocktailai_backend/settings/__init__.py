from .base import *

# Import the appropriate settings file based on the environment
from decouple import config

env = config('DJANGO_SETTINGS_MODULE', default='cocktailai_backend.settings.dev')

if env == 'cocktailai_backend.settings.dev':
    from .dev import *
elif env == 'cocktailai_backend.settings.prod':
    from .prod import * 