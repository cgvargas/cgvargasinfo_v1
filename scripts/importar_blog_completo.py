"""
Importacao completa do blog via RSS paginado do Wix -> Django/Supabase
Busca automaticamente todas as paginas ate nao encontrar posts novos.
Execute: python scripts/importar_blog_completo.py
"""
import os, sys, re, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from email.utils import parsedate_to_datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgvargas.settings')

import django
django.setup()

import cloudinary
import cloudinary.uploader
from django.utils.text import slugify
from django.contrib.auth.models import User
from blog.models import Post, Autor, Categoria


def fetch_rss(url, tentativas=3):
    """Busca o XML do RSS com retry e headers de browser."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
    }
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode('utf-8')
        except Exception as e:
            print(f"    Tentativa {i+1}/{tentativas} falhou: {e}")
            if i < tentativas - 1:
                time.sleep(3)
    return None


def extrair_posts_rss(xml_str):
    """Extrai lista de dicts com dados de cada post do XML RSS."""
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as e:
        print(f"    Erro ao parsear XML: {e}")
        return []

    posts = []
    for item in root.findall('.//item'):
        guid = item.findtext('guid', '').strip()
        titulo = item.findtext('title', '').strip()
        resumo = item.findtext('description', '').strip()
        link = item.findtext('link', '').strip()
        pub_date = item.findtext('pubDate', '').strip()
        categorias = [c.text for c in item.findall('category') if c.text]
        enclosure = item.find('enclosure')
        img_url = ''
        if enclosure is not None:
            raw = enclosure.get('url', '')
            # pega URL base sem parametros de resize do wix
            img_url = re.sub(r'/v1/fit/.*$', '', raw)
            # so imagens, nao videos
            if 'video.wixstatic' in img_url or raw.endswith('.mp4'):
                img_url = ''

        if guid and titulo:
            posts.append({
                'guid': guid,
                'titulo': titulo,
                'resumo': resumo,
                'link': link,
                'pub_date': pub_date,
                'categorias': categorias,
                'img_url': img_url,
            })
    return posts


def upload_imagem(url, public_id):
    if not url or not url.startswith('http'):
        return None
    try:
        res = cloudinary.uploader.upload(
            url, folder="cgvargas/blog",
            public_id=public_id, overwrite=False,
            resource_type="image"
        )
        return res['public_id']
    except Exception as e:
        print(f"      Aviso upload: {e}")
        return None


def slug_unico(titulo):
    base = slugify(titulo)[:180]
    slug = base
    i = 1
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def get_ou_criar_autor():
    autor = Autor.objects.first()
    if autor:
        return autor
    return Autor.objects.create(
        nome="Claudio Vargas",
        cargo="Fundador & Desenvolvedor",
        bio="Fundador da CGVargas Informatica, especialista em TI e desenvolvimento web.",
    )


def get_ou_criar_categoria(nome):
    slug_cat = slugify(nome)[:50] or 'sem-categoria'
    try:
        cat, _ = Categoria.objects.get_or_create(slug=slug_cat, defaults={'nome': nome})
        return cat
    except Exception:
        return None


def coletar_todos_posts(base_url, max_paginas=10):
    """
    Coleta posts de todas as paginas do RSS.
    O Wix retorna sempre os mesmos 20 na paginacao padrao,
    mas tenta offset/count alternativo para pegar todos.
    """
    todos = {}  # guid -> post dict (deduplicado por guid)

    # Tenta variantes de URL para pegar mais posts
    urls_para_tentar = [
        base_url,
        f"{base_url}?size=100",
        f"{base_url}?count=100",
        f"{base_url}?limit=100",
        f"{base_url}?pageSize=100",
    ]

    for url in urls_para_tentar:
        print(f"\n  Buscando: {url}")
        xml = fetch_rss(url)
        if not xml:
            print(f"  Falhou.")
            continue
        posts = extrair_posts_rss(xml)
        novos = 0
        for p in posts:
            if p['guid'] not in todos:
                todos[p['guid']] = p
                novos += 1
        print(f"  Encontrados {len(posts)} posts | {novos} novos | Total: {len(todos)}")
        time.sleep(1)

    return list(todos.values())


def main():
    print("\n" + "="*60)
    print("IMPORTACAO COMPLETA DO BLOG WIX -> DJANGO/SUPABASE")
    print("="*60)

    BASE_RSS = "https://www.cgvargas.com.br/blog-feed.xml"
    autor = get_ou_criar_autor()
    print(f"Autor: {autor.nome}")

    print("\nColetando posts do RSS...")
    posts = coletar_todos_posts(BASE_RSS)
    print(f"\nTotal de posts unicos coletados: {len(posts)}")

    if not posts:
        print("Nenhum post encontrado. Verifique a conexao com o Wix.")
        return

    criados = 0
    ignorados = 0
    erros = 0

    print(f"\n{'='*60}")
    print("Importando posts...")
    print(f"{'='*60}")

    for i, p in enumerate(posts, 1):
        titulo = p['titulo']
        print(f"\n[{i:02d}/{len(posts)}] {titulo[:65]}")

        # Verifica duplicata por titulo
        if Post.objects.filter(titulo=titulo).exists():
            print(f"       Ja existe, pulando.")
            ignorados += 1
            continue

        slug = slug_unico(titulo)

        # Data
        data_pub = None
        if p['pub_date']:
            try:
                data_pub = parsedate_to_datetime(p['pub_date'])
            except Exception:
                pass

        # Conteudo
        conteudo = (
            f"<p>{p['resumo']}</p>\n\n"
            f"<p><em>Artigo migrado do blog anterior. "
            f"<a href='{p['link']}' target='_blank' rel='noopener'>Ver original</a></em></p>"
        )

        # Upload imagem
        imagem_id = None
        if p['img_url']:
            print(f"       Upload imagem...")
            imagem_id = upload_imagem(p['img_url'], f"cgvargas/blog/{slug}")
            if imagem_id:
                print(f"       OK")

        try:
            # Categoria principal (primeira da lista)
            cat = None
            if p['categorias']:
                cat = get_ou_criar_categoria(p['categorias'][0])

            post = Post(
                titulo=titulo,
                slug=slug,
                resumo=p['resumo'][:300] if p['resumo'] else titulo[:200],
                conteudo=conteudo,
                publicado=True,
                autor=autor,
                categoria=cat,
            )
            if imagem_id:
                post.imagem_capa = imagem_id
            post.save()

            # data_criacao e auto_now_add — atualiza via queryset
            if data_pub:
                Post.objects.filter(pk=post.pk).update(data_criacao=data_pub)

            criados += 1
            print(f"       Criado: /blog/{slug}/")
        except Exception as e:
            print(f"       ERRO: {e}")
            erros += 1

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {criados} criados | {ignorados} ja existiam | {erros} erros")
    print(f"Ver em: http://127.0.0.1:8000/blog/")
    print(f"{'='*60}\n")

    if len(posts) < 48:
        restantes = 48 - criados - ignorados
        if restantes > 0:
            print(f"ATENCAO: O RSS do Wix so retornou {len(posts)} posts.")
            print(f"Os {restantes} posts restantes so podem ser obtidos via:")
            print(f"  1. Exportacao CSV pelo painel manage.wix.com")
            print(f"  2. Copiar/colar o conteudo de cada post manualmente")
            print(f"  3. Aguardar o site voltar e usar scraping com browser")


if __name__ == '__main__':
    main()
