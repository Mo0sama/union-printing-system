import os
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp')
ALLOWED_DOCUMENT_EXTENSIONS = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv')
ALLOWED_DESIGN_EXTENSIONS = (
    '.pdf', '.ai', '.eps', '.cdr', '.psd', '.tif', '.tiff',
    '.png', '.jpg', '.jpeg', '.svg', '.indd',
)
ALLOWED_IMAGE_MIMETYPES = ('image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml')
ALLOWED_DOCUMENT_MIMETYPES = (
    'application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain', 'text/csv',
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB


def validate_file_extension(allowed_extensions):
    def validator(value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                f'غير مسموح بهذا النوع من الملفات. الأنواع المسموحة: {", ".join(allowed_extensions)}'
            )
    return validator


def validate_file_size(max_size):
    def validator(value):
        if value.size > max_size:
            raise ValidationError(
                f'حجم الملف كبير جداً. الحد الأقصى: {filesizeformat(max_size)}'
            )
    return validator


validate_design_file = validate_file_extension(ALLOWED_DESIGN_EXTENSIONS)
validate_image_file = validate_file_extension(ALLOWED_IMAGE_EXTENSIONS)
validate_document_file = validate_file_extension(ALLOWED_DOCUMENT_EXTENSIONS)
validate_file_size_10mb = validate_file_size(MAX_FILE_SIZE)
validate_image_size_5mb = validate_file_size(MAX_IMAGE_SIZE)
