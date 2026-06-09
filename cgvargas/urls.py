from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection


def ping(request):
    """Health check endpoint para manter Render e Supabase ativos via UptimeRobot."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "error"
    return JsonResponse({"status": "ok", "db": db_status})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ping/', ping, name='ping'),
    path('', include('core.urls', namespace='core')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('portfolio/', include('portfolio.urls', namespace='portfolio')),
    path('glossario/', include('glossario.urls', namespace='glossario')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Configuração do Admin
admin.site.site_header = 'CGVargas — Painel Administrativo'
admin.site.site_title = 'CGVargas Admin'
admin.site.index_title = 'Gerenciamento do Site'
