from django.core.cache import cache
from django.http import HttpResponseBadRequest
from functools import wraps
from django.conf import settings
from .models import UserProfile

def get_plan_limits(plan):
    limits = {
        'basic': {'annotations': 10, 'uploads': 5, 'projects': 1, 'images': 100},
        'admin': {'annotations': 50, 'uploads': 20, 'projects': 5, 'images': 500},
        'licensed': {'annotations': 200, 'uploads': 100, 'projects': 20, 'images': 2000},
        'host': {'annotations': float('inf'), 'uploads': float('inf'), 'projects': float('inf'), 'images': float('inf')},
    }
    return limits.get(plan, limits['basic'])

def rate_limit(action='default', time_window=3600):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseBadRequest('Login required')
            
            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return HttpResponseBadRequest('Profile not set up')
            
            # Host bypass
            if profile.is_host or request.META.get('HTTP_HOST') == 'localhost:8000':
                return view_func(request, *args, **kwargs)
            
            # Plan limits
            limits = get_plan_limits(profile.nexify_plan)
            if limits[action] == float('inf'):
                return view_func(request, *args, **kwargs)
            
            cache_key = f"rate_{action}_{request.user.id}"
            count = cache.get(cache_key, 0)
            
            if count >= limits[action]:
                return HttpResponseBadRequest(f'Rate limit exceeded for {action}. Plan: {profile.nexify_plan}')
            
            cache.set(cache_key, count + 1, time_window)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

