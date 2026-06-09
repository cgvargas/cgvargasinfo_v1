from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from blog.models import Post
from portfolio.models import Projeto


def home(request):
    posts_recentes = Post.objects.filter(publicado=True)[:3]
    projetos_destaque = Projeto.objects.filter(destaque=True)[:4]
    return render(request, 'core/home.html', {
        'posts_recentes': posts_recentes,
        'projetos_destaque': projetos_destaque,
    })


def sobre(request):
    return render(request, 'core/sobre.html')


def servicos(request):
    return render(request, 'core/servicos.html')


def hardware(request):
    return render(request, 'core/hardware.html')


def privacidade(request):
    return render(request, 'core/privacidade.html')


def contato(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        assunto = request.POST.get('assunto', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()

        if nome and email and mensagem:
            try:
                send_mail(
                    subject=f'[CGVargas Site] {assunto or "Nova mensagem de contato"}',
                    message=f'Nome: {nome}\nEmail: {email}\n\nMensagem:\n{mensagem}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            except Exception:
                messages.error(request, 'Erro ao enviar mensagem. Por favor, tente novamente ou nos contate diretamente por email.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')

    return render(request, 'core/contato.html')
