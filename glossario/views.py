from django.shortcuts import render
from .models import Termo, CategoriaGlossario
from django.db.models import Q


def index(request):
    termos = Termo.objects.select_related('categoria').all().order_by('palavra')
    
    # Calculate statistics
    total_termos = termos.count()
    # 10 categories + 1 for "Todos" = 11
    total_categorias = CategoriaGlossario.objects.count() + 1
    novos_count = termos.filter(is_novo=True).count()
    atualizado_ano = 2026  # Current project year
    
    categorias = CategoriaGlossario.objects.all().order_by('nome')
    
    return render(request, 'glossario/index.html', {
        'termos': termos,
        'categorias': categorias,
        'total_termos': total_termos,
        'total_categorias': total_categorias,
        'novos_count': novos_count,
        'atualizado_ano': atualizado_ano,
    })

