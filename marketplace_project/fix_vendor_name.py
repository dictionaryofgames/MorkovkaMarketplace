import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'marketplace_project.settings'
django.setup()
from users.models import Vendor
for v in Vendor.objects.all():
    if not v.name or v.name.strip() == '':
        v.name = f"Магазин пользователя {v.owner_id}"
        v.save()
        print(f"Fixed: id={v.id} name='{v.name}'")
    else:
        print(f"OK: id={v.id} name='{v.name}'")
