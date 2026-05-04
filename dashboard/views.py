from jango.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import SourceFile
from nexify.models import NexifyWorkspace, NexifyProject, NexifyAssignment, NexifyDatasetVersion
import subprocess
import urllib.request
import urllib.error
import numpy as np

def is_admin(user):
    return user.is_staff or user.is_superuser

def get_ai_status():
    status = {'llm': 'Ollama', 'available': False, 'detail': 'unknown'}
    try:
        resp = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=3)
        if resp.status == 200:
            status['available'] = True
            status['detail'] = 'Local Ollama instance reachable'
    except Exception as e:
        status['detail'] = str(e)
    return status

@login_required
def home(request):
    stats = {
        'workspaces': NexifyWorkspace.objects.filter(owner=request.user).count(),
        'projects': NexifyProject.objects.filter(workspace__owner=request.user).count(),
        'users': NexifyAssignment.objects.filter(project__workspace__owner=request.user).values('user').distinct().count(),
        'datasets': NexifyDatasetVersion.objects.filter(project__workspace__owner=request.user).count(),
    }
    knowledge_stats = {'total': 0, 'docs': 0, 'scripts': 0}
    projects = []
    source_stats = SourceFile.objects.aggregate(total=Count('id'))
    knowledge_sources = SourceFile.objects.filter(is_knowledge_relevant=True).order_by('-last_updated')[:8]
    ai_status = get_ai_status()

    context = {
        'stats': stats,
        'knowledge_stats': knowledge_stats,
        'projects': projects,
        'source_stats': source_stats,
        'knowledge_sources': knowledge_sources,
        'ai_status': ai_status,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'dashboard.html', context)

@login_required
def projects_list(request):
    query = request.GET.get('q', '')
    projects = KnowledgeEntry.objects.filter(knowledge_type='doc')
    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(content_preview__icontains=query))
    projects = projects.order_by('-created_at')[:20]
    context = {'projects': projects, 'query': query}
    return render(request, 'dashboard.html', {'section': 'projects', 'projects': projects})

@login_required
def project_detail(request, project_id):
    project = KnowledgeEntry.objects.get(id=project_id)
    related_sources = SourceFile.objects.filter(path__icontains=project.title[:50]).order_by('-last_updated')[:10]
    context = {
        'project': project,
        'related_sources': related_sources,
    }
    return render(request, 'dashboard.html', {'section': 'project', 'project': project})

@login_required
def knowledge(request):
    query = request.GET.get('q', '')
    entries = KnowledgeEntry.objects.all()
    if query:
        entries = entries.filter(
            Q(title__icontains=query) | Q(content_preview__icontains=query)
        )
    entries = entries.order_by('-created_at')[:50]
    stats = KnowledgeEntry.objects.aggregate(
        total=Count('id'),
        docs=Count('id', filter=Q(knowledge_type='doc')),
        scripts=Count('id', filter=Q(knowledge_type='script'))
    )
    sources = SourceFile.objects.filter(is_knowledge_relevant=True).order_by('-last_updated')[:20]
    context = {'entries': entries, 'stats': stats, 'sources': sources, 'query': query}
    return render(request, 'knowledge.html', context)

@require_http_methods(["POST"])
def sync(request):
    subprocess.call(['python', 'tasks_fixed_standalone.py'], cwd='.')
    return JsonResponse({'status': 'synced', 'message': 'Knowledge base updated'})

@login_required
def agent(request):
    return render(request, 'agent.html')

@login_required
def tensorboard(request):
    return render(request, 'tensorboard.html')

def api_sensor(request):
    return JsonResponse({'sensor1': np.random.rand()*100, 'sensor2': np.random.rand()*100})

def api_projects(request):
    projects = KnowledgeEntry.objects.filter(knowledge_type='doc').values('id', 'title', 'created_at', 'content_preview')[:10]
    return JsonResponse({'projects': list(projects)})
