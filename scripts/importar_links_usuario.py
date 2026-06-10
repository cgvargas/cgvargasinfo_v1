"""
Importador de links selecionados do blog Wix para Django/Supabase
Execute: python scripts/importar_links_usuario.py
"""
import os, sys, re, time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgvargas.settings')

import django
django.setup()

import cloudinary.uploader
from django.utils.text import slugify
from blog.models import Post, Autor, Categoria

URLS = [
    "https://www.cgvargas.com.br/single-post/entendendo-o-gitignore-gerenciando-o-rastreamento-de-arquivos-no-git",
    "https://www.cgvargas.com.br/single-post/entendendo-o-padr%C3%A3o-grasp-expert-especialista-uma-abordagem-para-o-design-de-software",
    "https://www.cgvargas.com.br/single-post/explorando-a-programa%C3%A7%C3%A3o-paralela-para-an%C3%A1lise-de-dados-em-grande-escala",
    "https://www.cgvargas.com.br/single-post/explorando-o-potencial-da-biblioteca-python-yfinance-para-an%C3%A1lise-de-dados-financeiros",
    "https://www.cgvargas.com.br/single-post/explorando-as-ides-para-desenvolvimento-em-python-encontre-a-ferramenta-ideal-para-voc%C3%AA",
    "https://www.cgvargas.com.br/single-post/2017/12/18/voc%C3%AA-sabia-que-seu-teclado-pode-ser-remapeado",
    "https://www.cgvargas.com.br/single-post/2017/10/04/vers%C3%A3o-pc-de-forza-motorsport-7",
    "https://www.cgvargas.com.br/single-post/2017/09/16/ssd-versus-hdd",
    "https://www.cgvargas.com.br/single-post/2017/09/07/informa%C3%A7%C3%A3o-sobre-o-whatsapp-business",
    "https://www.cgvargas.com.br/single-post/2017/08/19/n%C3%A3o-use-um-computador-desprotegido",
    "https://www.cgvargas.com.br/single-post/2017/08/17/fiquem-atentos-pois-os-arquivos-do-power-point-tamb%C3%A9m-podem-conter-malware",
    "https://www.cgvargas.com.br/single-post/2017/08/07/investimento-em-tecnologia-empresarial",
    "https://www.cgvargas.com.br/single-post/2017/07/24/se%C3%A7%C3%A3o-nostalgia",
    "https://www.cgvargas.com.br/single-post/2017/07/22/aprendendo-a-desenhar-em-um-tablet",
    "https://www.cgvargas.com.br/single-post/2017/07/20/raz%C3%B5es-para-trocar-a-tela-de-notebook-quebrada",
    "https://www.cgvargas.com.br/single-post/2017/06/29/sabia-que-%C3%A9-poss%C3%ADvel-usar-o-shell-bash-do-linux-ubuntu-no-windows-10",
    "https://www.cgvargas.com.br/single-post/2017/06/21/o-teclado-e-seus-segredos",
    "https://www.cgvargas.com.br/single-post/2017/06/20/cuidados-com-os-teclados",
    "https://www.cgvargas.com.br/single-post/2017/06/19/curiosidades-sobre-o-teclado-de-computador",
    "https://www.cgvargas.com.br/single-post/2017/06/17/xbox-one-x-projeto-scorpio",
    "https://www.cgvargas.com.br/single-post/2017/06/16/o-que-%C3%A9-um-designer-de-jogos",
    "https://www.cgvargas.com.br/single-post/2017/06/06/musica-e-desenho",
    "https://www.cgvargas.com.br/single-post/2017/06/06/dicas-de-seguran%C3%A7a",
    "https://www.cgvargas.com.br/single-post/2017/03/07/requisitos-de-sistema-no-mundo-dos-animes"
]

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

        # Data de publicacao
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
        print(f"    Erro ao extrair {url}: {e}")
        return None

def main():
    from playwright.sync_api import sync_playwright
    from datetime import datetime

    print("\n" + "="*60)
    print("MIGRAÇÃO DE LINKS DO BLOG WIX -> DJANGO/SUPABASE")
    print("="*60)

    # Fase 1: Coleta dados do autor e banco
    autor = get_autor()
    if not autor:
        # Tenta criar se não existir
        autor = Autor.objects.create(
            nome="Claudio Vargas",
            cargo="Fundador & Desenvolvedor",
            bio="Especialista em TI e fundador da CGVargas Informática.",
        )
        print(f"Autor criado: {autor.nome}")
    else:
        print(f"Autor: {autor.nome}")

    slugs_existentes = set(Post.objects.values_list('slug', flat=True))
    titulos_existentes = set(Post.objects.values_list('titulo', flat=True))
    print(f"Posts no banco atualmente: {len(slugs_existentes)}")

    # Filtra URLs que ainda não foram importadas
    urls_para_importar = []
    for url in URLS:
        slug_url = slugify(url.rstrip('/').split('/')[-1])[:60]
        # verifica se ja existe por slug ou correspondência próxima
        ja_existe = any(slug_url[:30] in s or s[:30] in slug_url for s in slugs_existentes)
        if not ja_existe:
            urls_para_importar.append(url)

    print(f"Total de URLs: {len(URLS)}")
    print(f"URLs já importadas / ignoradas: {len(URLS) - len(urls_para_importar)}")
    print(f"URLs a importar agora: {len(urls_para_importar)}")

    if not urls_para_importar:
        print("Todos os posts já estão importados!")
        return

    dados_coletados = []

    # Fase 2: Playwright para scraping
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

        for i, url in enumerate(urls_para_importar, 1):
            print(f"[{i:02d}/{len(urls_para_importar)}] Extraindo: {url}")
            dados = extrair_post(page, url)
            if dados and dados.get('titulo'):
                dados_coletados.append(dados)
                print(f"    Título: {dados['titulo'][:60]}")
            else:
                print(f"    Falhou.")

        browser.close()

    # Fase 3: Importação no Django ORM
    print(f"\n{'='*60}")
    print(f"Importando {len(dados_coletados)} posts no banco...")
    print(f"{'='*60}")

    criados = 0
    ignorados = 0
    erros = 0

    for dados in dados_coletados:
        titulo = dados['titulo']

        if titulo in titulos_existentes:
            print(f"  Já existe: {titulo[:60]}")
            ignorados += 1
            continue

        slug = slug_unico(titulo)

        # Data
        data_pub = None
        try:
            ds = dados.get('data_str', '')
            if ds:
                if 'T' in ds:
                    data_pub = datetime.fromisoformat(ds.replace('Z', '+00:00'))
                else:
                    # tenta outros formatos ou usa date.today
                    data_pub = datetime.strptime(ds[:10], '%Y-%m-%d')
        except Exception:
            pass

        # Resumo
        texto = re.sub(r'<[^>]+>', ' ', dados.get('conteudo', ''))
        texto = re.sub(r'\s+', ' ', texto).strip()
        resumo = texto[:300] or titulo[:200]

        # Categoria
        cat = None
        if dados.get('categorias'):
            cat = get_ou_criar_categoria(dados['categorias'][0])

        # Upload imagem
        imagem_id = None
        img = re.sub(r'/v1/fit/.*$', '', dados.get('img_url', ''))
        if img and img.startswith('http'):
            print(f"  Subindo imagem para: {titulo[:40]}...")
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
            print(f"  ✅ Criado: /blog/{slug}/")
        except Exception as e:
            print(f"  ❌ ERRO: {e}")
            erros += 1

    print(f"\n{'='*60}")
    print(f"CONCLUÍDO: {criados} criados | {ignorados} ignorados | {erros} erros")
    print(f"Total no banco agora: {Post.objects.count()} posts")
    print(f"Ver: http://127.0.0.1:8000/blog/")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
