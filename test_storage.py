import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieR.settings")
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage

print("DEFAULT FILE STORAGE:", default_storage)
print("aaaaaaaaaaaa:", os.getenv("MINIO_STORAGE_MEDIA_URL"))