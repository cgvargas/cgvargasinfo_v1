from django.shortcuts import render, get_object_or_404
from .models import Projeto, Tecnologia


def lista(request):
    projetos = Projeto.objects.all()
    tecnologias = Tecnologia.objects.filter(projetos__isnull=False).distinct()
    tech_filter = request.GET.get('tech')

    if tech_filter:
        projetos = projetos.filter(tecnologias__nome__iexact=tech_filter)

    return render(request, 'portfolio/lista.html', {
        'projetos': projetos,
        'tecnologias': tecnologias,
        'tech_filter': tech_filter,
    })


def detalhe(request, slug):
    projeto = get_object_or_404(
        Projeto.objects.prefetch_related('imagens', 'videos', 'tecnologias'), 
        slug=slug
    )
    outros_projetos = Projeto.objects.exclude(pk=projeto.pk)[:3]

    return render(request, 'portfolio/detalhe.html', {
        'projeto': projeto,
        'outros_projetos': outros_projetos,
    })

