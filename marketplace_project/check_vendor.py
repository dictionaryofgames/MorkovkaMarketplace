import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'marketplace_project.settings'
django.setup()
from users.models import Vendor
for v in Vendor.objects.all():
    print(f"id={v.id} name='{v.name}' slug={v.slug}")
