from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
import datetime
from django.views.decorators.csrf import csrf_exempt

def dashboard_view(request):
    return render(request, 'dashboard.html')

@csrf_exempt
def api_sensor(request):
    if request.method == 'GET':
        # Mock Celery update every min
        data = {
            'sensors': [{'id':1, 'value': 25.5, 'type': 'temp'}],
            'build': 'Updated at ' + str(datetime.datetime.now()),
            'camera': 'stream_url_mock',
            'annotation': 'ready',
            'automation': 'idle',
            'sandbox': 'test',
            'spider_data': {'table': 'wrangled data'}
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'GET only'}, status=405)
