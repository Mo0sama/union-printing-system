import shutil
import tarfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup SQLite database and media files'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', default=str(Path.home() / 'union_backups'),
                            help='Backup directory (default: ~/union_backups)')
        parser.add_argument('--keep-days', '-k', type=int, default=7,
                            help='Delete backups older than N days (default: 7)')

    def handle(self, *args, **options):
        backup_dir = Path(options['output'])
        backup_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Database
        db_path = settings.BASE_DIR.parent / 'data' / 'db.sqlite3'
        if db_path.exists():
            db_dest = backup_dir / f'db_{date_str}.sqlite3'
            shutil.copy2(str(db_path), str(db_dest))
            self.stdout.write(self.style.SUCCESS(f'DB backup: {db_dest}'))
        else:
            self.stdout.write(self.style.WARNING(f'Database not found: {db_path}'))

        # Media files
        media_dir = settings.BASE_DIR / 'media'
        if media_dir.exists():
            media_dest = backup_dir / f'media_{date_str}.tar.gz'
            with tarfile.open(str(media_dest), 'w:gz') as tar:
                tar.add(str(media_dir), arcname='media')
            self.stdout.write(self.style.SUCCESS(f'Media backup: {media_dest}'))
        else:
            self.stdout.write(self.style.WARNING(f'Media directory not found: {media_dir}'))

        # Clean old backups
        keep = options['keep_days']
        cutoff = datetime.now().timestamp() - keep * 86400
        for f in backup_dir.glob('*'):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                self.stdout.write(f'Deleted old backup: {f.name}')

        self.stdout.write(self.style.SUCCESS('Backup complete'))
