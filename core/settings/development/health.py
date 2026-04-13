import logging
import time
from django.db import connection
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

logger = logging.getLogger('api')

@never_cache
@csrf_exempt
def health_check(request):
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': int(time.time()),
        'environment': getattr(settings, 'DJANGO_ENV', 'unknown'),
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        overall_healthy = False
        logger.error(f"Health check database failure: {e}")
    
    # Cache health check
    try:
        cache_key = 'health_check_test'
        cache_value = 'test_value'
        cache.set(cache_key, cache_value, 30)
        retrieved_value = cache.get(cache_key)
        
        if retrieved_value == cache_value:
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache read/write successful'
            }
        else:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'message': 'Cache read/write failed'
            }
            overall_healthy = False
            
        cache.delete(cache_key)
        
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'warning',
            'message': f'Cache check failed: {str(e)}'
        }
        logger.warning(f"Health check cache failure: {e}")
    
    # Storage health check
    try:
        # Check if media directory is writable
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            test_file = os.path.join(media_root, '.health_check_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            health_status['checks']['storage'] = {
                'status': 'healthy',
                'message': 'Storage read/write successful'
            }
        else:
            health_status['checks']['storage'] = {
                'status': 'warning',
                'message': 'Media directory not configured or missing'
            }
            
    except Exception as e:
        health_status['checks']['storage'] = {
            'status': 'unhealthy',
            'message': f'Storage check failed: {str(e)}'
        }
        overall_healthy = False
        logger.error(f"Health check storage failure: {e}")
    
    # Email health check (only in production)
    if getattr(settings, 'DJANGO_ENV', 'local') == 'production':
        try:
            # Test email configuration without actually sending
            from django.core.mail import get_connection
            email_connection = get_connection()
            email_connection.open()
            email_connection.close()
            
            health_status['checks']['email'] = {
                'status': 'healthy',
                'message': 'Email configuration valid'
            }
        except Exception as e:
            health_status['checks']['email'] = {
                'status': 'unhealthy',
                'message': f'Email configuration failed: {str(e)}'
            }
            overall_healthy = False
            logger.error(f"Health check email failure: {e}")
    
    # Memory and disk usage (basic checks)
    try:
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        health_status['checks']['system'] = {
            'status': 'healthy' if memory_percent < 90 and disk_percent < 90 else 'warning',
            'memory_usage': f"{memory_percent:.1f}%",
            'disk_usage': f"{disk_percent:.1f}%"
        }
        
        if memory_percent > 95 or disk_percent > 95:
            overall_healthy = False
            
    except ImportError:
        health_status['checks']['system'] = {
            'status': 'unknown',
            'message': 'psutil not installed for system monitoring'
        }
    except Exception as e:
        health_status['checks']['system'] = {
            'status': 'error',
            'message': f'System check failed: {str(e)}'
        }
        logger.error(f"Health check system failure: {e}")
    
    # Response time
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    health_status['response_time_ms'] = round(response_time, 2)
    
    # Overall status
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
    elif any(check.get('status') == 'warning' for check in health_status['checks'].values()):
        health_status['status'] = 'degraded'
    
    # HTTP status code based on health
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


@never_cache
@csrf_exempt
def ready_check(request):
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': int(time.time())
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not ready',
            'error': str(e),
            'timestamp': int(time.time())
        }, status=503)


@never_cache
@csrf_exempt  
def live_check(request):
    return JsonResponse({
        'status': 'alive',
        'timestamp': int(time.time())
    })