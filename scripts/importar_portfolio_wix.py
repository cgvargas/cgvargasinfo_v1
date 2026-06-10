"""
Importação direta do portfólio do Wix para Django/Supabase
Execute: python scripts/importar_portfolio_wix.py
"""
import os, sys, re, json
from pathlib import Path
from datetime import datetime, date

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgvargas.settings')

import django
django.setup()

import cloudinary
import cloudinary.uploader
from django.utils.text import slugify
from portfolio.models import Projeto, ImagemProjeto


def wix_url_to_https(wix_src):
    """Converte wix:image://v1/SLUG/filename.ext para URL pública do Wixstatic."""
    if not wix_src:
        return None
    # Extrai o slug da imagem: tudo entre /v1/ e /filename
    match = re.search(r'wix:image://v1/([^/]+)/', wix_src)
    if match:
        slug = match.group(1)
        return f"https://static.wixstatic.com/media/{slug}"
    return None


def upload_imagem(url, public_id):
    """Faz upload para Cloudinary e retorna o public_id do Cloudinary."""
    if not url:
        return None
    try:
        print(f"    📤 Upload: {url[:70]}...")
        res = cloudinary.uploader.upload(
            url,
            folder="cgvargas/portfolio",
            public_id=public_id,
            overwrite=False,
            resource_type="image"
        )
        print(f"    ✅ OK → {res['secure_url']}")
        return res['public_id']
    except Exception as e:
        print(f"    ⚠️  Erro no upload: {e}")
        return None


# ── Dados extraídos diretamente do CSV colado pelo usuário ────────────────────

PROJETOS = [
    {
        "nome": "CG.BookStore.Online",
        "slug": "cgbookstore-online",
        "descricao": (
            "CG.BookStore.Online é uma aplicação web desenvolvida pela CGVargas Informática, "
            "voltada para leitores que buscam uma experiência personalizada de descoberta literária. "
            "Oferece recursos como prateleiras customizadas, recomendações inteligentes, busca "
            "integrada ao Google Books, detalhamento com vídeos e um modelo freemium com upgrade "
            "premium. Com arquitetura moderna em Django e foco em usabilidade, a plataforma combina "
            "tecnologia e literatura para transformar o modo como as pessoas se conectam com livros."
        ),
        "descricao_curta": "Plataforma de descoberta literária com prateleiras, recomendações e Google Books.",
        "cliente": "CG.BookStore.Online",
        "data_conclusao": date(2025, 12, 2),
        "destaque": True,
        "ordem": 1,
        "imagem_principal_wix": "wix:image://v1/41a0d9_e275202c50ba4bcfab7ba29829023ec6~mv2.jpg/home_edited.jpg#originWidth=1031&originHeight=573",
        "galeria_wix": [
            {"slug": "41a0d9_8b68821163d74fa7996ed69bfa03873d~mv2.png", "legenda": "Tela 1"},
            {"slug": "41a0d9_6fc37b1d8fb84a878a73d9af9962f88e~mv2.png", "legenda": "Tela 2"},
            {"slug": "41a0d9_588a1b081ec54f7c8d9eb5dab1521db6~mv2.png", "legenda": "Tela 3"},
            {"slug": "41a0d9_5844ad94447a49dea48cb4d8b6f3a408~mv2.png", "legenda": "Tela 4"},
            {"slug": "41a0d9_8b4cb54db21f4994bcb0cda4ffaa0cd8~mv2.png", "legenda": "Tela 5"},
            {"slug": "41a0d9_77f4181c230d4a9c913c50333121b0f3~mv2.png", "legenda": "Tela 6"},
        ],
    },
    {
        "nome": "Essência Verde Naturalle",
        "slug": "essencia-verde-naturalle",
        "descricao": (
            "Essência Verde Naturalle é um restaurante digital com foco em alimentação saudável "
            "e personalizada. A aplicação permite navegar por um cardápio nutritivo, visualizar "
            "pratos com informações nutricionais, fazer pedidos online e conhecer a filosofia "
            "natural do restaurante. Tudo com uma interface leve, intuitiva e voltada ao bem-estar."
        ),
        "descricao_curta": "Restaurante digital com cardápio nutritivo, pedidos online e foco em bem-estar.",
        "cliente": "Naturalle Alimentos",
        "data_conclusao": date(2025, 12, 2),
        "destaque": True,
        "ordem": 2,
        "imagem_principal_wix": "wix:image://v1/41a0d9_2103c9687010445f91dc3fd6d0ffc35b~mv2.png/Ess%C3%AAncia%20Verde%20pag.png#originWidth=1366&originHeight=768",
        "galeria_wix": [
            {"slug": "41a0d9_6659e4e8a0e9493e85c3c23ad766c912~mv2.png", "legenda": "naturalle2"},
            {"slug": "41a0d9_3f0c2ab72dc641b6b3d5e2fc47c0bf22~mv2.png", "legenda": "naturalle"},
            {"slug": "41a0d9_657f30da07074468a6496d79ac4d9590~mv2.png", "legenda": "naturalle3"},
            {"slug": "41a0d9_3f903e4fb9f8449eab7ae0c75a9ad97f~mv2.png", "legenda": "naturalle4"},
        ],
    },
    {
        "nome": "SOS Cartões",
        "slug": "sos-cartoes",
        "descricao": (
            "SOS Cartões é uma aplicação web de controle financeiro pessoal com foco em cartões "
            "de crédito. Permite o upload de extratos, geração automática de gráficos, planilhas "
            "e relatórios com ações recomendadas. A plataforma também oferece cotações de moedas "
            "em tempo real e um feed com as principais notícias do mundo financeiro, ajudando o "
            "usuário a tomar decisões mais conscientes e estratégicas."
        ),
        "descricao_curta": "Controle financeiro pessoal: extratos, gráficos, relatórios e cotações em tempo real.",
        "cliente": "Level Cards Financial",
        "data_conclusao": date(2025, 12, 2),
        "destaque": True,
        "ordem": 3,
        "imagem_principal_wix": "wix:image://v1/41a0d9_a7b5bd772f0b4452b5e665d89c16690a~mv2.png/ChatGPT%20Image%2030%20de%20jun.%20de%202025,%2009_35_09.png#originWidth=1536&originHeight=1024",
        "galeria_wix": [
            {"slug": "41a0d9_13449a6b103449d1bdea397fcb86d4df~mv2.png", "legenda": "cards02"},
            {"slug": "41a0d9_591b8dddf610434e8558577ef930708c~mv2.png", "legenda": "cards03"},
            {"slug": "41a0d9_c748fd4f78a04e049f05f4f94d2f7f4d~mv2.png", "legenda": "cards04"},
            {"slug": "41a0d9_89a37428cef64a5683e9868afdf1b4ef~mv2.png", "legenda": "cards05"},
        ],
    },
]


def main():
    print("\n" + "="*60)
    print("🗂️  IMPORTANDO PORTFÓLIO DO WIX → DJANGO/SUPABASE")
    print("="*60)

    criados = 0
    atualizados = 0

    for dados in PROJETOS:
        nome = dados["nome"]
        slug = dados["slug"]

        print(f"\n{'─'*50}")
        print(f"📁 Projeto: {nome}")

        # Verifica se já existe
        projeto, criado = Projeto.objects.get_or_create(
            slug=slug,
            defaults={
                "nome": nome,
                "descricao": dados["descricao"],
                "descricao_curta": dados["descricao_curta"],
                "destaque": dados["destaque"],
                "data_conclusao": dados["data_conclusao"],
                "ordem": dados["ordem"],
            }
        )

        if not criado:
            print(f"  ℹ️  Já existe — atualizando descrição e dados...")
            projeto.descricao = dados["descricao"]
            projeto.descricao_curta = dados["descricao_curta"]
            projeto.destaque = dados["destaque"]
            projeto.data_conclusao = dados["data_conclusao"]
            projeto.ordem = dados["ordem"]

        # Upload da imagem principal
        if not projeto.imagem:
            url_principal = wix_url_to_https(dados["imagem_principal_wix"])
            if url_principal:
                public_id = upload_imagem(url_principal, f"cgvargas/portfolio/{slug}/capa")
                if public_id:
                    projeto.imagem = public_id

        projeto.save()
        print(f"  ✅ Projeto salvo: /portfolio/{slug}/")

        # Upload das imagens da galeria
        imagens_existentes = projeto.imagens.count()
        if imagens_existentes == 0:
            print(f"  🖼️  Enviando {len(dados['galeria_wix'])} imagens da galeria...")
            for ordem, img in enumerate(dados["galeria_wix"], 1):
                img_slug = img["slug"]
                url = f"https://static.wixstatic.com/media/{img_slug}"
                public_id = upload_imagem(url, f"cgvargas/portfolio/{slug}/galeria_{ordem:02d}")
                if public_id:
                    ImagemProjeto.objects.create(
                        projeto=projeto,
                        imagem=public_id,
                        legenda=img.get("legenda", ""),
                        ordem=ordem
                    )
        else:
            print(f"  ⏭️  Galeria já tem {imagens_existentes} imagens, pulando upload.")

        if criado:
            criados += 1
        else:
            atualizados += 1

    print(f"\n{'='*60}")
    print(f"✅ Concluído: {criados} criados | {atualizados} atualizados")
    print(f"🌐 Veja em: http://127.0.0.1:8000/portfolio/")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
