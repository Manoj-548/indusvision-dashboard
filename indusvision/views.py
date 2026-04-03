from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
import datetime
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect


def login_view(request):
    from django.contrib.auth.forms import UserCreationForm
    register = request.POST.get('register') == '1' if request.method == 'POST' else False
    if register:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard/')
    else:
        form = AuthenticationForm(request, data=request.POST if request.method == 'POST' else None)
        if form and form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard/')
    return render(request, 'login.html', {'form': form, 'register': register})


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
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
