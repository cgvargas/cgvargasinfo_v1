from django.contrib import admin
from .models import Post, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ['nome']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'publicado', 'data_criacao']
    list_filter = ['publicado', 'categoria', 'data_criacao']
    search_fields = ['titulo', 'resumo', 'conteudo']
    prepopulated_fields = {'slug': ('titulo',)}
    list_editable = ['publicado']
    date_hierarchy = 'data_criacao'
    fieldsets = (
        ('Conteúdo', {
            'fields': ('titulo', 'slug', 'resumo', 'conteudo', 'imagem_capa')
        }),
        ('Classificação', {
            'fields': ('categoria', 'publicado')
        }),
    )
