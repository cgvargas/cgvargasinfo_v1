from django.db import models


class CategoriaGlossario(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Termo(models.Model):
    palavra = models.CharField(max_length=150, unique=True)
    subtitulo = models.CharField(max_length=200, blank=True, null=True)
    definicao = models.TextField()
    categoria = models.ForeignKey(
        CategoriaGlossario, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='termos'
    )
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Tags separadas por vírgula")
    is_novo = models.BooleanField(default=False)
    letra = models.CharField(max_length=1, editable=False, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Termo'
        verbose_name_plural = 'Termos'
        ordering = ['palavra']

    def save(self, *args, **kwargs):
        self.letra = self.palavra[0].upper()
        super().save(*args, **kwargs)

    @property
    def tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def __str__(self):
        return self.palavra


