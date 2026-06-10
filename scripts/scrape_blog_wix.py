"""
Scraping completo do blog Wix com Playwright -> Django/Supabase
Captura todos os posts que ainda nao foram importados.
Execute: python scripts/scrape_blog_wix.py
"""
import os, sys, re, time, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgvargas.settings')

import django
django.setup()

import cloudinary.uploader
from django.utils.text import slugify
from blog.models import Post, Autor, Categoria

BLOG_URL = "https://www.cgvargas.com.br/blog"


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


def get_autor():
    return Autor.objects.first()


def get_ou_criar_categoria(nome):
    if not nome:
        return None
    slug_cat = slugify(nome)[:50] or 'sem-categoria'
    try:
        cat, _ = Categoria.objects.get_or_create(
            slug=slug_cat, defaults={'nome': nome}
        )
        return cat
    except Exception:
        return None


def coletar_links_blog(page):
    """Abre o blog e coleta todos os links de posts com scroll agressivo."""
    print(f"\nAbrindo: {BLOG_URL}")
    page.goto(BLOG_URL, wait_until="load", timeout=60000)
    try:
        page.wait_for_selector('a[href*="/single-post/"]', timeout=15000)
    except Exception:
        pass
    time.sleep(5)

    links = set()

    def coletar_links_pagina():
        """Coleta todos os links visíveis com múltiplos seletores."""
        seletores = [
            'a[href*="/single-post/"]',
            'a[href*="single-post"]',
            '[data-hook*="post"] a',
            '.post-list-item a',
            'article a',
        ]
        for sel in seletores:
            try:
                els = page.query_selector_all(sel)
                for el in els:
                    href = el.get_attribute('href') or ''
                    if 'single-post' in href:
                        if href.startswith('/'):
                            href = 'https://www.cgvargas.com.br' + href
                        if href.startswith('http'):
                            links.add(href.split('#')[0].split('?')[0])
            except Exception:
                pass

    # Scroll progressivo — 30 vezes com pausas
    ultima_contagem = 0
    sem_mudanca = 0

    for rodada in range(30):
        coletar_links_pagina()

        # Scroll para o final
        page.evaluate("window.scrollBy(0, 800)")
        time.sleep(2)

        # A cada 5 rodadas, scroll completo até o fim
        if rodada % 5 == 4:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)

        print(f"  Scroll {rodada+1}: {len(links)} links")

        # Para se não encontrar mais links novos em 5 tentativas
        if len(links) == ultima_contagem:
            sem_mudanca += 1
            if sem_mudanca >= 5:
                # Tenta botão "Ver mais" / "Load more"
                try:
                    btn = page.locator(
                        'button:has-text("Ver mais"), button:has-text("Load more"), '
                        'button:has-text("Carregar mais"), [data-hook="load-more-button"]'
                    ).first
                    if btn.is_visible():
                        btn.click()
                        time.sleep(3)
                        sem_mudanca = 0
                        continue
                except Exception:
                    pass
                print(f"  Sem novos links por {sem_mudanca} tentativas. Encerrando scroll.")
                break
        else:
            sem_mudanca = 0

        ultima_contagem = len(links)

    # Coleta final
    coletar_links_pagina()
    print(f"\nTotal de links únicos encontrados: {len(links)}")
    return list(links)


def extrair_post(page, url):
    """Acessa um post individual e extrai titulo, conteudo, imagem, data."""
    try:
        page.goto(url, wait_until="load", timeout=60000)
        try:
            page.wait_for_selector('h1', timeout=10000)
        except Exception:
            pass
        time.sleep(3)

        # Titulo
        titulo = ''
        for sel in ['h1', '[data-hook="post-title"]', '.post-title', 'article h1']:
            el = page.query_selector(sel)
            if el:
                titulo = el.inner_text().strip()
                if titulo:
                    break

        if not titulo:
            # fallback: pega do titulo da pagina
            titulo = page.title().split('|')[0].strip()

        # Conteudo principal
        conteudo_html = ''
        for sel in [
            '[data-hook="post-body"]',
            '.post-content',
            'article .content',
            'main article',
            '.blog-post-content',
        ]:
            el = page.query_selector(sel)
            if el:
                conteudo_html = el.inner_html()
                if len(conteudo_html) > 100:
                    break

        # Texto simples como fallback
        if not conteudo_html:
            for sel in ['article', 'main', '.post-body']:
                el = page.query_selector(sel)
                if el:
                    conteudo_html = f"<p>{el.inner_text()}</p>"
                    break

        # Imagem de capa (og:image e meta)
        img_url = ''
        try:
            img_url = page.evaluate(
                "document.querySelector('meta[property=\"og:image\"]')?.content || ''"
            )
        except Exception:
            pass

        # Data de publicacao (meta og:article:published_time)
        data_str = ''
        try:
            data_str = page.evaluate(
                "document.querySelector('meta[property=\"article:published_time\"]')?.content || "
                "document.querySelector('time')?.getAttribute('datetime') || ''"
            )
        except Exception:
            pass

        # Categorias/tags
        categorias = []
        try:
            tags_els = page.query_selector_all('[data-hook="tag"], .post-tags a, [class*="tag"]')
            categorias = [el.inner_text().strip() for el in tags_els if el.inner_text().strip()]
        except Exception:
            pass

        return {
            'titulo': titulo,
            'conteudo': conteudo_html or f'<p>Post importado de <a href="{url}">{url}</a></p>',
            'img_url': img_url,
            'data_str': data_str,
            'categorias': categorias,
            'url_original': url,
        }

    except Exception as e:
        print(f"    Erro ao extrair: {e}")
        return None


def main():
    from playwright.sync_api import sync_playwright
    from datetime import datetime

    print("\n" + "="*60)
    print("SCRAPING COMPLETO DO BLOG WIX -> DJANGO/SUPABASE")
    print("="*60)

    # ── FASE 1: Coleta dados do banco ANTES de abrir o Playwright ────────────
    autor = get_autor()
    if not autor:
        print("ERRO: Nenhum autor encontrado. Execute importar_blog_completo.py primeiro.")
        return

    slugs_existentes  = set(Post.objects.values_list('slug', flat=True))
    titulos_existentes = set(Post.objects.values_list('titulo', flat=True))
    print(f"Posts ja no banco: {len(slugs_existentes)}")

    # ── FASE 2: Playwright — zero ORM aqui ───────────────────────────────────
    dados_coletados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            viewport={'width': 1280, 'height': 900}
        )
        page = context.new_page()

        # 2a. Coleta todos os links
        print("\n--- Coletando links dos posts ---")
        links = coletar_links_blog(page)

        # Filtra apenas novos
        links_novos = []
        for link in links:
            slug_url = slugify(link.rstrip('/').split('/')[-1])[:60]
            ja_existe = any(slug_url[:30] in s or s[:30] in slug_url
                            for s in slugs_existentes)
            if not ja_existe:
                links_novos.append(link)

        print(f"Links novos: {len(links_novos)} de {len(links)} total")

        # 2b. Extrai conteudo de cada post novo
        print("\n--- Extraindo posts novos ---")
        for i, url in enumerate(links_novos, 1):
            print(f"\n[{i:02d}/{len(links_novos)}] {url}")
            dados = extrair_post(page, url)
            if dados and dados.get('titulo'):
                dados_coletados.append(dados)
                print(f"    OK: {dados['titulo'][:60]}")
            else:
                print(f"    Falhou.")

        browser.close()

    # ── FASE 3: Importa no Django — FORA do Playwright ───────────────────────
    print(f"\n{'='*60}")
    print(f"Importando {len(dados_coletados)} posts...")
    print(f"{'='*60}")

    criados = 0
    ignorados = 0
    erros = 0

    for dados in dados_coletados:
        titulo = dados['titulo']

        if titulo in titulos_existentes:
            print(f"  Ja existe: {titulo[:60]}")
            ignorados += 1
            continue

        slug = slug_unico(titulo)

        # Data
        data_pub = None
        try:
            ds = dados.get('data_str', '')
            if ds and 'T' in ds:
                data_pub = datetime.fromisoformat(ds.replace('Z', '+00:00'))
        except Exception:
            pass

        # Resumo
        texto = re.sub(r'<[^>]+>', ' ', dados.get('conteudo', ''))
        texto = re.sub(r'\s+', ' ', texto).strip()
        resumo = texto[:300] or titulo[:200]

        # Categoria
        cat = get_ou_criar_categoria(dados['categorias'][0]) if dados.get('categorias') else None

        # Upload imagem
        imagem_id = None
        img = re.sub(r'/v1/fit/.*$', '', dados.get('img_url', ''))
        if img and img.startswith('http'):
            print(f"  Imagem: {titulo[:40]}...")
            imagem_id = upload_imagem(img, f"cgvargas/blog/{slug}")

        try:
            post = Post(
                titulo=titulo, slug=slug,
                resumo=resumo,
                conteudo=dados.get('conteudo') or f'<p>{resumo}</p>',
                publicado=True, autor=autor, categoria=cat,
            )
            if imagem_id:
                post.imagem_capa = imagem_id
            post.save()
            if data_pub:
                Post.objects.filter(pk=post.pk).update(data_criacao=data_pub)
            titulos_existentes.add(titulo)
            criados += 1
            print(f"  Criado: /blog/{slug}/")
        except Exception as e:
            print(f"  ERRO: {e}")
            erros += 1

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {criados} criados | {ignorados} ignorados | {erros} erros")
    print(f"Total no banco: {Post.objects.count()} posts")
    print(f"Ver: http://127.0.0.1:8000/blog/")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
