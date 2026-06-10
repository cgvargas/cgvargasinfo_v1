"""
Script de importação: Wix CSV → Django (Supabase)
================================================
Como usar:
  1. Exporte os posts do Blog do Wix como CSV (painel manage.wix.com)
  2. Exporte os projetos do Portfólio do Wix como CSV
  3. Coloque os arquivos nesta pasta (scripts/)
  4. Execute:
       python scripts/importar_wix.py --blog blog_wix.csv
       python scripts/importar_wix.py --portfolio portfolio_wix.csv
       python scripts/importar_wix.py --blog blog_wix.csv --portfolio portfolio_wix.csv
"""

import os
import sys
import csv
import re
import argparse
import django
import requests
from pathlib import Path
from datetime import datetime

# ── Configura o Django ───────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgvargas.settings')
django.setup()

import cloudinary
import cloudinary.uploader
from django.utils.text import slugify
from django.contrib.auth.models import User


# ── Helpers ──────────────────────────────────────────────────────────────────

def limpar_html(texto):
    """Remove tags HTML básicas e limpa espaços."""
    if not texto:
        return ''
    texto = re.sub(r'<[^>]+>', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def fazer_upload_imagem(url_imagem, public_id=None):
    """Faz upload de uma imagem para o Cloudinary a partir de uma URL."""
    if not url_imagem or not url_imagem.startswith('http'):
        return None
    try:
        print(f"  📤 Enviando imagem para Cloudinary: {url_imagem[:60]}...")
        resultado = cloudinary.uploader.upload(
            url_imagem,
            folder="cgvargas/migrado_wix",
            public_id=public_id,
            overwrite=False,
            resource_type="image"
        )
        url_nova = resultado.get('secure_url')
        print(f"  ✅ Imagem enviada: {url_nova}")
        return url_nova
    except Exception as e:
        print(f"  ⚠️  Erro ao enviar imagem: {e}")
        return url_imagem  # retorna URL original como fallback


def gerar_slug_unico(modelo, titulo, campo_slug='slug'):
    """Gera um slug único verificando colisões no banco."""
    slug_base = slugify(titulo)
    slug = slug_base
    contador = 1
    while modelo.objects.filter(**{campo_slug: slug}).exists():
        slug = f"{slug_base}-{contador}"
        contador += 1
    return slug


def parse_data(texto_data):
    """Tenta parsear datas em vários formatos comuns."""
    if not texto_data:
        return None
    formatos = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d/%m/%Y %H:%M',
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(texto_data.strip(), fmt)
        except ValueError:
            continue
    print(f"  ⚠️  Não foi possível parsear a data: '{texto_data}'")
    return None


def mostrar_colunas(caminho_csv):
    """Exibe as colunas do CSV para mapeamento manual."""
    with open(caminho_csv, newline='', encoding='utf-8-sig') as f:
        leitor = csv.DictReader(f)
        colunas = leitor.fieldnames
        print(f"\n📋 Colunas encontradas no CSV '{caminho_csv}':")
        for i, col in enumerate(colunas):
            print(f"  [{i}] {col}")
        print()
        # mostra primeira linha como exemplo
        for linha in leitor:
            print("📄 Exemplo da primeira linha:")
            for col in colunas:
                valor = linha.get(col, '')
                print(f"  {col}: {valor[:80]}{'...' if len(valor) > 80 else ''}")
            break


# ── Importação do Blog ────────────────────────────────────────────────────────

def importar_blog(caminho_csv):
    """Importa posts do CSV exportado do Wix para o modelo Post do Django."""
    from blog.models import Post, Autor

    print(f"\n{'='*60}")
    print(f"📰 IMPORTANDO BLOG: {caminho_csv}")
    print(f"{'='*60}")

    # Primeiro mostra as colunas para diagnóstico
    mostrar_colunas(caminho_csv)

    # Autor padrão: busca o primeiro superusuário ou cria um
    autor_django = None
    try:
        autor_obj = Autor.objects.first()
        if not autor_obj:
            user = User.objects.filter(is_superuser=True).first()
            if user:
                autor_obj = Autor.objects.create(
                    nome="CGVargas Informática",
                    bio="Equipe CGVargas",
                    usuario=user
                )
        autor_django = autor_obj
    except Exception as e:
        print(f"⚠️  Aviso: não foi possível configurar autor: {e}")

    criados = 0
    ignorados = 0

    with open(caminho_csv, newline='', encoding='utf-8-sig') as f:
        leitor = csv.DictReader(f)

        for i, linha in enumerate(leitor, 1):
            # ── Mapeamento de campos (ajuste se necessário) ──
            # O Wix pode usar nomes diferentes dependendo do idioma do painel
            titulo = (
                linha.get('title') or linha.get('Title') or
                linha.get('Título') or linha.get('titulo') or ''
            ).strip()

            conteudo_raw = (
                linha.get('content') or linha.get('Content') or
                linha.get('body') or linha.get('Body') or
                linha.get('Conteúdo') or linha.get('conteudo') or ''
            )

            resumo_raw = (
                linha.get('excerpt') or linha.get('Excerpt') or
                linha.get('description') or linha.get('Description') or
                linha.get('Resumo') or linha.get('resumo') or ''
            )

            imagem_url = (
                linha.get('coverImage') or linha.get('cover_image') or
                linha.get('image') or linha.get('Image') or
                linha.get('Imagem') or linha.get('featured_image') or ''
            ).strip()

            data_raw = (
                linha.get('publishedDate') or linha.get('published_date') or
                linha.get('createdDate') or linha.get('created_date') or
                linha.get('Data') or linha.get('date') or ''
            )

            tags_raw = (
                linha.get('tags') or linha.get('Tags') or
                linha.get('categories') or ''
            )

            if not titulo:
                print(f"  ⚠️  Linha {i}: título vazio, pulando.")
                ignorados += 1
                continue

            print(f"\n[{i}] Importando: {titulo[:60]}")

            # Verifica se já existe
            slug = gerar_slug_unico(Post, titulo)
            if Post.objects.filter(titulo=titulo).exists():
                print(f"  ⏭️  Já existe, pulando.")
                ignorados += 1
                continue

            # Processa conteúdo
            conteudo = limpar_html(conteudo_raw) if conteudo_raw else ''
            resumo = limpar_html(resumo_raw)[:500] if resumo_raw else titulo[:200]

            # Data de publicação
            data_pub = parse_data(data_raw)

            # Upload da imagem de capa
            imagem_cloudinary = None
            if imagem_url:
                imagem_cloudinary = fazer_upload_imagem(
                    imagem_url,
                    public_id=f"cgvargas/blog/{slug}"
                )

            # Cria o post
            try:
                kwargs = dict(
                    titulo=titulo,
                    slug=slug,
                    resumo=resumo,
                    conteudo=conteudo or resumo,
                    publicado=True,
                )
                if data_pub:
                    kwargs['criado_em'] = data_pub
                if autor_django:
                    kwargs['autor'] = autor_django
                if imagem_cloudinary:
                    kwargs['imagem'] = imagem_cloudinary

                post = Post(**kwargs)
                post.save()
                criados += 1
                print(f"  ✅ Post criado: /blog/{slug}/")

            except Exception as e:
                print(f"  ❌ Erro ao criar post: {e}")
                ignorados += 1

    print(f"\n{'='*60}")
    print(f"📰 Blog: {criados} posts criados | {ignorados} ignorados")
    print(f"{'='*60}\n")


# ── Importação do Portfólio ───────────────────────────────────────────────────

def importar_portfolio(caminho_csv):
    """Importa projetos do CSV exportado do Wix para o modelo Projeto do Django."""
    from portfolio.models import Projeto

    print(f"\n{'='*60}")
    print(f"🗂️  IMPORTANDO PORTFÓLIO: {caminho_csv}")
    print(f"{'='*60}")

    mostrar_colunas(caminho_csv)

    criados = 0
    ignorados = 0

    with open(caminho_csv, newline='', encoding='utf-8-sig') as f:
        leitor = csv.DictReader(f)

        for i, linha in enumerate(leitor, 1):
            # ── Mapeamento de campos ──
            titulo = (
                linha.get('title') or linha.get('Title') or
                linha.get('Título') or linha.get('nome') or
                linha.get('Nome') or ''
            ).strip()

            descricao_raw = (
                linha.get('description') or linha.get('Description') or
                linha.get('Descrição') or linha.get('descricao') or
                linha.get('content') or ''
            )

            imagem_url = (
                linha.get('image') or linha.get('Image') or
                linha.get('thumbnail') or linha.get('Thumbnail') or
                linha.get('Imagem') or linha.get('coverImage') or ''
            ).strip()

            tecnologias = (
                linha.get('tags') or linha.get('Tags') or
                linha.get('tecnologias') or linha.get('Tecnologias') or
                linha.get('stack') or ''
            )

            url_projeto = (
                linha.get('url') or linha.get('URL') or
                linha.get('link') or linha.get('Link') or ''
            ).strip()

            if not titulo:
                print(f"  ⚠️  Linha {i}: título vazio, pulando.")
                ignorados += 1
                continue

            print(f"\n[{i}] Importando projeto: {titulo[:60]}")

            if Projeto.objects.filter(titulo=titulo).exists():
                print(f"  ⏭️  Já existe, pulando.")
                ignorados += 1
                continue

            slug = gerar_slug_unico(Projeto, titulo)
            descricao = limpar_html(descricao_raw)

            # Upload da imagem
            imagem_cloudinary = None
            if imagem_url:
                imagem_cloudinary = fazer_upload_imagem(
                    imagem_url,
                    public_id=f"cgvargas/portfolio/{slug}"
                )

            try:
                kwargs = dict(
                    titulo=titulo,
                    slug=slug,
                    descricao=descricao or titulo,
                    destaque=True,
                )
                if tecnologias:
                    kwargs['tecnologias'] = tecnologias
                if url_projeto:
                    kwargs['url_projeto'] = url_projeto
                if imagem_cloudinary:
                    kwargs['imagem'] = imagem_cloudinary

                projeto = Projeto(**kwargs)
                projeto.save()
                criados += 1
                print(f"  ✅ Projeto criado: /portfolio/{slug}/")

            except Exception as e:
                print(f"  ❌ Erro ao criar projeto: {e}")
                print(f"     Verifique os campos do modelo Projeto em portfolio/models.py")
                ignorados += 1

    print(f"\n{'='*60}")
    print(f"🗂️  Portfólio: {criados} projetos criados | {ignorados} ignorados")
    print(f"{'='*60}\n")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Importa conteúdo do Wix (CSV) para o Django CGVargas'
    )
    parser.add_argument('--blog', metavar='ARQUIVO.csv',
                        help='CSV do blog exportado do Wix')
    parser.add_argument('--portfolio', metavar='ARQUIVO.csv',
                        help='CSV do portfólio exportado do Wix')
    parser.add_argument('--inspecionar', metavar='ARQUIVO.csv',
                        help='Apenas mostra as colunas do CSV sem importar')
    args = parser.parse_args()

    if not any([args.blog, args.portfolio, args.inspecionar]):
        parser.print_help()
        print("\n💡 Exemplo:")
        print("   python scripts/importar_wix.py --blog scripts/blog_wix.csv")
        print("   python scripts/importar_wix.py --portfolio scripts/portfolio_wix.csv")
        print("   python scripts/importar_wix.py --inspecionar scripts/arquivo.csv")
        sys.exit(0)

    if args.inspecionar:
        mostrar_colunas(args.inspecionar)
        sys.exit(0)

    if args.blog:
        if not Path(args.blog).exists():
            print(f"❌ Arquivo não encontrado: {args.blog}")
            sys.exit(1)
        importar_blog(args.blog)

    if args.portfolio:
        if not Path(args.portfolio).exists():
            print(f"❌ Arquivo não encontrado: {args.portfolio}")
            sys.exit(1)
        importar_portfolio(args.portfolio)

    print("🎉 Importação concluída!")


if __name__ == '__main__':
    main()
