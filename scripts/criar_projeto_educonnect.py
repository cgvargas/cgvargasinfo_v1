"""
Cria o projeto EduConnect no portfólio Django.
Faz upload das imagens para o Cloudinary e salva o projeto no banco.
As imagens estão em static/img/portfolio/educonnect/ (versionadas no git).

Execute: python scripts/criar_projeto_educonnect.py
"""
import os
import sys
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgvargas.settings')

import django
django.setup()

import cloudinary
import cloudinary.uploader
from portfolio.models import Projeto, ImagemProjeto, Tecnologia

# ── Caminhos das imagens (dentro do repositório git) ─────────────────────────
ARTIFACTS_DIR = BASE_DIR / "static" / "img" / "portfolio" / "educonnect"

IMAGENS = [
    {
        "arquivo": ARTIFACTS_DIR / "dashboard.png",
        "legenda": "Dashboard Principal — Visão geral com KPIs e gráficos de desempenho",
        "ordem": 1,
        "public_id": "cgvargas/portfolio/educonnect/dashboard",
        "is_capa": True,
    },
    {
        "arquivo": ARTIFACTS_DIR / "alunos.png",
        "legenda": "Gestão de Alunos — Listagem com notas, frequência e status",
        "ordem": 2,
        "public_id": "cgvargas/portfolio/educonnect/alunos",
        "is_capa": False,
    },
    {
        "arquivo": ARTIFACTS_DIR / "notas.png",
        "legenda": "Lançamento de Notas — Grade de avaliações por bimestre",
        "ordem": 3,
        "public_id": "cgvargas/portfolio/educonnect/notas",
        "is_capa": False,
    },
    {
        "arquivo": ARTIFACTS_DIR / "calendario.png",
        "legenda": "Calendário Escolar — Agenda integrada com eventos e grade de horários",
        "ordem": 4,
        "public_id": "cgvargas/portfolio/educonnect/calendario",
        "is_capa": False,
    },
]

PROJETO_DADOS = {
    "nome": "EduConnect — Sistema de Gestão Escolar",
    "slug": "educonnect-sistema-gestao-escolar",
    "descricao": (
        "EduConnect é uma aplicação web completa para gestão de instituições de ensino, "
        "desenvolvida com foco em usabilidade, performance e experiência do usuário. "
        "A plataforma centraliza toda a gestão escolar: cadastro e acompanhamento de alunos, "
        "professores e turmas, lançamento de notas por bimestre com visualização de desempenho, "
        "controle de frequência, calendário escolar integrado com eventos e provas, "
        "e um dashboard executivo com KPIs e gráficos em tempo real. "
        "Com controle de acesso por perfil (Administrador, Professor e Aluno), "
        "o sistema garante segurança e privacidade dos dados. "
        "Desenvolvida com Python/Django no backend e interface moderna e responsiva no frontend, "
        "a aplicação foi projetada para escolas de todos os tamanhos."
    ),
    "descricao_curta": "Plataforma web completa para gestão escolar: alunos, notas, frequência, calendário e relatórios.",
    "url_projeto": "",
    "url_repositorio": "",
    "destaque": True,
    "data_conclusao": date(2025, 6, 1),
    "ordem": 4,
}

TECNOLOGIAS = [
    "Python",
    "Django",
    "PostgreSQL",
    "JavaScript",
    "HTML5",
    "CSS3",
    "Cloudinary",
    "Docker",
]


def upload_imagem_local(caminho_arquivo, public_id):
    """Faz upload de um arquivo local para o Cloudinary."""
    if not caminho_arquivo.exists():
        print(f"    ❌ Arquivo não encontrado: {caminho_arquivo}")
        return None
    try:
        print(f"    📤 Upload: {caminho_arquivo.name}")
        res = cloudinary.uploader.upload(
            str(caminho_arquivo),
            folder="",           # public_id já tem o caminho completo
            public_id=public_id,
            overwrite=True,
            resource_type="image",
        )
        print(f"    ✅ OK → {res['secure_url']}")
        return res["public_id"]
    except Exception as e:
        print(f"    ⚠️  Erro no upload: {e}")
        return None


def garantir_tecnologias(nomes):
    """Garante que as tecnologias existam e retorna os objetos."""
    techs = []
    for nome in nomes:
        tech, criada = Tecnologia.objects.get_or_create(nome=nome)
        if criada:
            print(f"  🔧 Tecnologia criada: {nome}")
        techs.append(tech)
    return techs


def main():
    print("\n" + "=" * 60)
    print("🎓  CRIANDO PROJETO EDUCONNECT NO PORTFÓLIO")
    print("=" * 60)

    slug = PROJETO_DADOS["slug"]

    # ── 1. Criar ou buscar o projeto ────────────────────────────────
    print(f"\n📁 Projeto: {PROJETO_DADOS['nome']}")
    projeto, criado = Projeto.objects.get_or_create(
        slug=slug,
        defaults={
            "nome": PROJETO_DADOS["nome"],
            "descricao": PROJETO_DADOS["descricao"],
            "descricao_curta": PROJETO_DADOS["descricao_curta"],
            "url_projeto": PROJETO_DADOS["url_projeto"],
            "url_repositorio": PROJETO_DADOS["url_repositorio"],
            "destaque": PROJETO_DADOS["destaque"],
            "data_conclusao": PROJETO_DADOS["data_conclusao"],
            "ordem": PROJETO_DADOS["ordem"],
        }
    )

    if not criado:
        print("  ℹ️  Projeto já existe — atualizando dados...")
        projeto.nome = PROJETO_DADOS["nome"]
        projeto.descricao = PROJETO_DADOS["descricao"]
        projeto.descricao_curta = PROJETO_DADOS["descricao_curta"]
        projeto.destaque = PROJETO_DADOS["destaque"]
        projeto.data_conclusao = PROJETO_DADOS["data_conclusao"]
        projeto.ordem = PROJETO_DADOS["ordem"]

    # ── 2. Upload das imagens ────────────────────────────────────────
    print(f"\n  🖼️  Processando {len(IMAGENS)} imagens...")

    for img_dados in IMAGENS:
        public_id = upload_imagem_local(img_dados["arquivo"], img_dados["public_id"])

        if not public_id:
            continue

        # Imagem de capa do projeto
        if img_dados["is_capa"] and not projeto.imagem:
            projeto.imagem = public_id
            print(f"  🖼️  Imagem de capa definida.")

        # Adiciona à galeria (evita duplicatas)
        if not projeto.imagens.filter(ordem=img_dados["ordem"]).exists():
            ImagemProjeto.objects.create(
                projeto=projeto,
                imagem=public_id,
                legenda=img_dados["legenda"],
                ordem=img_dados["ordem"],
            )
            print(f"  ✅ Galeria [{img_dados['ordem']}]: {img_dados['legenda'][:50]}")
        else:
            print(f"  ⏭️  Galeria [{img_dados['ordem']}] já existe, pulando.")

    # ── 3. Salvar projeto ────────────────────────────────────────────
    projeto.save()
    print(f"\n  ✅ Projeto salvo!")

    # ── 4. Tecnologias ───────────────────────────────────────────────
    print(f"\n  🔧 Associando tecnologias...")
    techs = garantir_tecnologias(TECNOLOGIAS)
    projeto.tecnologias.set(techs)
    print(f"  ✅ {len(techs)} tecnologias associadas.")

    # ── Resumo ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"✅ Projeto '{projeto.nome}' {'criado' if criado else 'atualizado'} com sucesso!")
    print(f"🌐 Veja em: http://127.0.0.1:8000/portfolio/{slug}/")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
