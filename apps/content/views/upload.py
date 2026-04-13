from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from uuid import uuid4

@staff_member_required
@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if uploaded_file.content_type not in allowed_types:
                return JsonResponse({
                    'error': 'Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed.'
                }, status=400)
            
            # Validate file size (max 5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'error': 'File size too large. Maximum size is 5MB.'
                }, status=400)
            
            # Generate unique filename
            file_ext = os.path.splitext(uploaded_file.name)[1]
            filename = f"{uuid4().hex}{file_ext}"
            
            # Save file using Django's default storage (works with S3/Spaces)
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile

            path = default_storage.save(f'blog/uploads/{filename}', ContentFile(uploaded_file.read()))
            file_url = default_storage.url(path)

            return JsonResponse({
                'location': file_url
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Error uploading file: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'error': 'No file provided'
    }, status=400)
