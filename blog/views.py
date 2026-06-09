from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Categoria


def lista(request):
    posts = Post.objects.filter(publicado=True)
    categoria_slug = request.GET.get('categoria')
    categoria_atual = None

    if categoria_slug:
        categoria_atual = get_object_or_404(Categoria, slug=categoria_slug)
        posts = posts.filter(categoria=categoria_atual)

    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts_paginados = paginator.get_page(page)
    categorias = Categoria.objects.all()

    return render(request, 'blog/lista.html', {
        'posts': posts_paginados,
        'categorias': categorias,
        'categoria_atual': categoria_atual,
    })


def detalhe(request, slug):
    post = get_object_or_404(Post, slug=slug, publicado=True)
    posts_relacionados = Post.objects.filter(
        publicado=True, categoria=post.categoria
    ).exclude(pk=post.pk)[:3]

    return render(request, 'blog/detalhe.html', {
        'post': post,
        'posts_relacionados': posts_relacionados,
    })
