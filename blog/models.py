from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Autor(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=150, blank=True, help_text="Ex: Especialista em TI, Desenvolvedor")
    foto = CloudinaryField('Foto de Perfil', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    github = models.URLField('GitHub URL', blank=True, null=True)
    linkedin = models.URLField('LinkedIn URL', blank=True, null=True)

    class Meta:
        verbose_name = 'Autor'
        verbose_name_plural = 'Autores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Post(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    resumo = models.TextField(max_length=300, help_text='Breve descrição para listagem e SEO')
    conteudo = CKEditor5Field('Conteúdo', config_name='default')
    imagem_capa = CloudinaryField('Imagem de Capa', blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='posts'
    )
    autor = models.ForeignKey(
        Autor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='posts'
    )
    publicado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:detalhe', kwargs={'slug': self.slug})
