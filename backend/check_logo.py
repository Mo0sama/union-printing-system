import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from apps.core.models import CompanySetting

s = CompanySetting.get_settings()
print(f'Logo field: {s.logo}')
if s.logo:
    print(f'Logo file name: {s.logo.name}')
    print(f'Logo path: {s.logo.path}')
    print(f'Logo exists: {os.path.exists(s.logo.path)}')
else:
    print('Logo is empty/null - no image uploaded')
