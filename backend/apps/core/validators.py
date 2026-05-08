import os
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


ALLOWED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp',
    '.pdf', '.ai', '.eps', '.cdr', '.psd', '.tif', '.tiff', '.indd',
    '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt',
    '.mp4', '.avi', '.mov', '.mkv', '.zip', '.rar', '.7z',
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'غير مسموح بهذا النوع من الملفات. الأنواع المسموحة: {", ".join(ALLOWED_EXTENSIONS)}'
        )


def validate_file_size(value):
    if value.size > MAX_FILE_SIZE:
        raise ValidationError(
            f'حجم الملف كبير جداً. الحد الأقصى: {filesizeformat(MAX_FILE_SIZE)}'
        )
