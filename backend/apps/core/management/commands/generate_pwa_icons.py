from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from apps.core.models import CompanySetting


class Command(BaseCommand):
    help = 'Generate PWA icons and favicon from the company logo'

    def handle(self, *args, **options):
        company = CompanySetting.get_settings()
        if not company.logo:
            self.stdout.write(self.style.ERROR('No logo uploaded in CompanySetting. Upload one first via /core/settings/'))
            return

        logo_path = company.logo.path
        img = Image.open(logo_path)

        sizes = {
            'static/images/icon-192x192.png': (192, 192),
            'static/images/icon-512x512.png': (512, 512),
            'static/images/favicon.png': (32, 32),
        }

        for rel_path, size in sizes.items():
            full_path = settings.BASE_DIR / rel_path
            resized = img.resize(size, Image.LANCZOS)
            resized.save(str(full_path), 'PNG')
            self.stdout.write(self.style.SUCCESS(f'Saved {rel_path}'))

        self.stdout.write(self.style.SUCCESS('PWA icons generated. Run collectstatic --noinput to deploy.'))
