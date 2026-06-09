from django.db import models
from cloudinary.models import CloudinaryField


class Tecnologia(models.Model):
    nome = models.CharField(max_length=80)
    icone = models.CharField(max_length=100, blank=True, help_text='Classe do ícone ou emoji')

    class Meta:
        verbose_name = 'Tecnologia'
        verbose_name_plural = 'Tecnologias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    descricao = models.TextField()
    descricao_curta = models.CharField(max_length=200, blank=True)
    tecnologias = models.ManyToManyField(Tecnologia, blank=True, related_name='projetos')
    url_projeto = models.URLField(blank=True, null=True, verbose_name='URL do Projeto')
    url_repositorio = models.URLField(blank=True, null=True, verbose_name='Repositório (GitHub)')
    imagem = CloudinaryField('Imagem do Projeto', blank=True, null=True)
    destaque = models.BooleanField(default=False, help_text='Exibir em destaque na homepage')
    data_conclusao = models.DateField(blank=True, null=True, verbose_name='Data de Conclusão')
    ordem = models.PositiveIntegerField(default=0, help_text='Ordem de exibição')

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['ordem', '-data_conclusao']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('portfolio:detalhe', kwargs={'slug': self.slug})
