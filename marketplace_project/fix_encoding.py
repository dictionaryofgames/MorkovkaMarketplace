import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'marketplace_project.settings'
django.setup()
from users.models import Vendor
for v in Vendor.objects.all():
    old = v.name
    v.name = f"Магазин пользователя {v.owner_id}"
    v.save()
    print(f"Changed: '{old}' -> '{v.name}'")
