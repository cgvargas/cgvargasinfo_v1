from django.contrib import admin
from .models import Termo, CategoriaGlossario


@admin.register(CategoriaGlossario)
class CategoriaGlossarioAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Termo)
class TermoAdmin(admin.ModelAdmin):
    list_display = ['palavra', 'letra', 'categoria', 'data_criacao']
    list_filter = ['letra', 'categoria']
    search_fields = ['palavra', 'definicao']
    readonly_fields = ['letra']
