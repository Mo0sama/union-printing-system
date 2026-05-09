#!/bin/bash
# Daily backup script for UNION-ERP (PythonAnywhere)
# 
# Scheduled task (paid PA): pythonanywhere.com → Tasks
# Manual run: bash deploy_pythonanywhere/backup.sh
# Via management command: python manage.py backup_db
#
# Free alternative: use cron-job.org to call a URL endpoint (see below)

cd ~/union-printing-system/backend || exit 1
source venv/bin/activate
python manage.py backup_db --output ~/union_backups --keep-days 7
