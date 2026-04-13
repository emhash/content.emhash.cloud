from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles import finders
import os
import time

@never_cache
@csrf_exempt
def static_files_debug(request):
    debug_info = {
        'timestamp': int(time.time()),
        'debug_mode': settings.DEBUG,
        'static_configuration': {
            'STATIC_URL': getattr(settings, 'STATIC_URL', 'Not set'),
            'STATIC_ROOT': str(getattr(settings, 'STATIC_ROOT', 'Not set')),
            'STATIC_ROOT_EXISTS': os.path.exists(getattr(settings, 'STATIC_ROOT', '')) if getattr(settings, 'STATIC_ROOT', None) else False,
            'STATICFILES_STORAGE': getattr(settings, 'STATICFILES_STORAGE', 'Not set'),
        },
        'media_configuration': {
            'MEDIA_URL': getattr(settings, 'MEDIA_URL', 'Not set'),
            'MEDIA_ROOT': str(getattr(settings, 'MEDIA_ROOT', 'Not set')),
            'MEDIA_ROOT_EXISTS': os.path.exists(getattr(settings, 'MEDIA_ROOT', '')) if getattr(settings, 'MEDIA_ROOT', None) else False,
        },
        'middleware': {
            'whitenoise_enabled': any('whitenoise' in middleware.lower() for middleware in settings.MIDDLEWARE),
            'middleware_list': settings.MIDDLEWARE,
        }
    }
    
    # Check if static files exist
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            files = os.listdir(static_root)
            debug_info['static_files'] = {
                'total_items': len(files),
                'sample_files': files[:10] if files else [],
                'admin_dir_exists': 'admin' in files,
            }
        else:
            debug_info['static_files'] = {'error': 'STATIC_ROOT does not exist'}
    except Exception as e:
        debug_info['static_files'] = {'error': str(e)}
    
    # Test admin static file discovery
    try:
        admin_css = finders.find('admin/css/base.css')
        debug_info['static_file_discovery'] = {
            'admin_css_found': bool(admin_css),
            'admin_css_path': admin_css if admin_css else None,
        }
    except Exception as e:
        debug_info['static_file_discovery'] = {'error': str(e)}
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})


@never_cache
@csrf_exempt  
def system_info(request):
    import sys
    
    info = {
        'timestamp': int(time.time()),
        'python_version': sys.version,
        'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
        'environment': getattr(settings, 'DJANGO_ENV', 'Unknown'),
        'settings_module': os.getenv('DJANGO_SETTINGS_MODULE', 'Unknown'),
        'base_dir': str(getattr(settings, 'BASE_DIR', 'Unknown')),
        'installed_apps': getattr(settings, 'INSTALLED_APPS', []),
    }
    
    return JsonResponse(info, json_dumps_params={'indent': 2}) 