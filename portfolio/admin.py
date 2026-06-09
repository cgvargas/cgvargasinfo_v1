from django.contrib import admin
from .models import Projeto, Tecnologia, ImagemProjeto, VideoProjeto


class ImagemProjetoInline(admin.TabularInline):
    model = ImagemProjeto
    extra = 1
    fields = ['imagem', 'legenda', 'ordem']


class VideoProjetoInline(admin.TabularInline):
    model = VideoProjeto
    extra = 1
    fields = ['video', 'youtube_url', 'titulo', 'ordem']


@admin.register(Tecnologia)
class TecnologiaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone']
    search_fields = ['nome']


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'destaque', 'ordem', 'data_conclusao']
    list_filter = ['destaque', 'tecnologias']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['destaque', 'ordem']
    filter_horizontal = ['tecnologias']
    inlines = [ImagemProjetoInline, VideoProjetoInline]
    fieldsets = (
        ('Informações', {
            'fields': ('nome', 'slug', 'descricao_curta', 'descricao', 'imagem')
        }),
        ('Links', {
            'fields': ('url_projeto', 'url_repositorio')
        }),
        ('Detalhes', {
            'fields': ('tecnologias', 'destaque', 'ordem', 'data_conclusao')
        }),
    )

