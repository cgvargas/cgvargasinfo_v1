from django.shortcuts import render
from .models import Termo, CategoriaGlossario
from django.db.models import Q


def index(request):
    busca = request.GET.get('q', '').strip()
    letra_filtro = request.GET.get('letra', '').upper()

    termos = Termo.objects.select_related('categoria').all()

    if busca:
        termos = termos.filter(
            Q(palavra__icontains=busca) | Q(definicao__icontains=busca)
        )
    elif letra_filtro:
        termos = termos.filter(letra=letra_filtro)

    # Letras disponíveis para navegação A-Z
    letras_com_termos = Termo.objects.values_list('letra', flat=True).distinct().order_by('letra')
    categorias = CategoriaGlossario.objects.all()

    return render(request, 'glossario/index.html', {
        'termos': termos,
        'busca': busca,
        'letra_filtro': letra_filtro,
        'letras_com_termos': list(letras_com_termos),
        'categorias': categorias,
        'alfabeto': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    })
