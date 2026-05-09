#!/bin/bash
# Daily backup script for UNION-ERP (PythonAnywhere)
# Schedule via: pythonanywhere.com → Dashboard → Tasks → Schedule
# Command: bash ~/union-printing-system/deploy_pythonanywhere/backup.sh
# Time: 03:00 daily

BACKUP_DIR=~/union_backups
PROJECT_DIR=~/union-printing-system
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup SQLite database
cp "$PROJECT_DIR/data/db.sqlite3" "$BACKUP_DIR/db_$DATE.sqlite3"

# Backup media files
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" -C "$PROJECT_DIR/backend" media

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "db_*.sqlite3" -mtime +7 -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
