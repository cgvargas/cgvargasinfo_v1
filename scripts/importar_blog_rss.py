"""
Importacao do blog via RSS do Wix -> Django/Supabase
Execute: python scripts/importar_blog_rss.py
"""
import os, sys, re, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
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
from blog.models import Post, Autor

# ── Dados extraidos do RSS do Wix ──────────────────────────────────────────

RSS_XML = r"""<?xml version="1.0" encoding="UTF-8"?><rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"><channel><title><![CDATA[CGVargas Informatica]]></title><description><![CDATA[cgvargas]]></description><link>https://www.cgvargas.com.br/blog</link><generator>RSS for Node</generator><item><title><![CDATA[Entre dois processadores: a historia real por tras da CGVargas Informatica]]></title><description><![CDATA[Aqui na CGVargas Informatica, nosso dia a dia e dividido entre o desenvolvimento de sistemas para web e a producao de conteudos para...]]></description><link>https://www.cgvargas.com.br/single-post/entre-dois-processadores-a-hist%C3%B3ria-real-por-tr%C3%A1s-da-cgvargas-inform%C3%A1tica</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Hardware]]></category><category><![CDATA[Artigo]]></category><pubDate>Mon, 14 Jul 2025 22:19:17 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_0c27780d48e941c0bca366f5a2b40b82~mv2.png/v1/fit/w_1000,h_1000,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Python: A Linguagem de Alto Nivel que Impulsiona a Inovacao]]></title><description><![CDATA[Desvendando o Poder do Python O Python e uma linguagem de programacao que se destaca por sua curva de aprendizado incrivelmente baixa,...]]></description><link>https://www.cgvargas.com.br/single-post/python-a-linguagem-de-alto-n%C3%ADvel-que-impulsiona-a-inova%C3%A7%C3%A3o</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Software]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Programacao]]></category><pubDate>Sun, 06 Jul 2025 17:58:27 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_e6a7a45fb86d4f24b4eab8879cf192df~mv2.png/v1/fit/w_1000,h_1000,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Inteligencia Artificial no Cotidiano: Como a IA Esta Transformando Nossas Vidas]]></title><description><![CDATA[A inteligencia artificial ja nao e mais coisa de filme de ficcao cientifica - ela esta presente no dia a dia de milhoes de pessoas,...]]></description><link>https://www.cgvargas.com.br/single-post/intelig%C3%AAncia-artificial-no-cotidiano-como-a-ia-est%C3%A1-transformando-nossas-vidas</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Software]]></category><category><![CDATA[Informacao]]></category><pubDate>Tue, 01 Jul 2025 01:17:45 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_cfc8178f8284421ea588d36ac7b10a8c~mv2.png/v1/fit/w_1000,h_1000,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Threads vs. vCPUs: Desvendando as Unidades de Processamento]]></title><description><![CDATA[No mundo da tecnologia, dois termos frequentemente encontrados ao explorar o funcionamento das CPUs e ambientes de virtualizacao sao...]]></description><link>https://www.cgvargas.com.br/single-post/threads-vs-vcpus-desvendando-as-unidades-de-processamento</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Hardware]]></category><category><![CDATA[Software]]></category><category><![CDATA[Artigo]]></category><pubDate>Sun, 05 Nov 2023 13:47:03 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_00fead339c5541bd85772201fd9a35c5~mv2.jpeg/v1/fit/w_1000,h_1000,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Abstracao e Decomposicao: Fundamentos Essenciais em Analise e Desenvolvimento de Sistemas]]></title><description><![CDATA[Introducao: Na jornada de estudo e pratica em Analise e Desenvolvimento de Sistemas (ADS), encontramos dois conceitos-chave que permeiam...]]></description><link>https://www.cgvargas.com.br/single-post/abstra%C3%A7%C3%A3o-e-decomposi%C3%A7%C3%A3o-fundamentos-essenciais-em-an%C3%A1lise-e-desenvolvimento-de-sistemas</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Artigo]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Software]]></category><pubDate>Thu, 14 Sep 2023 14:32:48 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_4cc15df5cd434c8d94ac51860eb744bd~mv2.png/v1/fit/w_748,h_200,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Como o Armazenamento de Filas Revoluciona o Processamento de Pedidos em Lojas Online]]></title><description><![CDATA[Gerenciar pedidos em uma loja online pode ser um desafio, especialmente durante picos de trafego. Felizmente, o armazenamento de filas...]]></description><link>https://www.cgvargas.com.br/single-post/como-o-armazenamento-de-filas-revoluciona-o-processamento-de-pedidos-em-lojas-online</link><category><![CDATA[Nuvem]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Artigo]]></category><category><![CDATA[Acervo Academico]]></category><pubDate>Mon, 28 Aug 2023 15:52:52 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_abcfb787f46f4fe6b3a27e950998a883~mv2.png/v1/fit/w_600,h_250,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Como Executar Aplicativos da Sua Maquina Fisica em uma Maquina Virtual]]></title><description><![CDATA[Se voce esta mergulhando no mundo da virtualizacao e deseja aproveitar ao maximo seus aplicativos, voce pode estar se perguntando como...]]></description><link>https://www.cgvargas.com.br/single-post/como-executar-aplicativos-da-sua-m%C3%A1quina-f%C3%ADsica-em-uma-m%C3%A1quina-virtual</link><category><![CDATA[Nuvem]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Acervo Academico]]></category><pubDate>Sun, 20 Aug 2023 17:27:58 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_0048515ab7204864b1c9c5202919108a~mv2.png/v1/fit/w_1000,h_777,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Explorando os Misterios Persas no Universo de Prince of Persia: The Lost Crown]]></title><description><![CDATA[Os amantes dos jogos de plataforma, preparem-se para uma jornada epica que transcende os limites do tempo e do espaco! A Ubisoft esta...]]></description><link>https://www.cgvargas.com.br/single-post/explorando-os-mist%C3%A9rios-persas-no-universo-de-prince-of-persia-the-lost-crown</link><category><![CDATA[Games]]></category><category><![CDATA[Noticias]]></category><category><![CDATA[Tecnologia]]></category><pubDate>Thu, 17 Aug 2023 19:12:29 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_fbec03fba0b648d6a9b40d3d8f4f1803~mv2.png/v1/fit/w_1000,h_720,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Gerenciando Espaco em Disco com o OneDrive: Dicas para Acessar Arquivos Offline]]></title><description><![CDATA[Se voce e um entusiasta da tecnologia, sabe como e importante otimizar o armazenamento no seu dispositivo. Com o OneDrive, voce pode...]]></description><link>https://www.cgvargas.com.br/single-post/gerenciando-espa%C3%A7o-em-disco-com-o-onedrive-dicas-para-acessar-arquivos-offline</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Dicas]]></category><category><![CDATA[Informacao]]></category><pubDate>Mon, 14 Aug 2023 19:10:21 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_fe5c6b6a93d5438082cf914aa435800c~mv2.png/v1/fit/w_920,h_340,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Explorando Programacao Orientada a Objetos em Java]]></title><description><![CDATA[Na jornada do aprendizado da programacao, a compreensao dos conceitos fundamentais e essencial. Um desses conceitos e a Programacao...]]></description><link>https://www.cgvargas.com.br/single-post/explorando-programa%C3%A7%C3%A3o-orientada-a-objetos-em-java</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Fri, 11 Aug 2023 20:29:40 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_484c2160e59849b08acd5e5059a7aad1~mv2.png/v1/fit/w_1000,h_853,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Virtualizacao Local X Computacao em Nuvem]]></title><description><![CDATA[O que e mais eficiente? virtualizar um sistema operacional diferente na maquina cliente ou um servico em nuvem para utilizar este mesmo...]]></description><link>https://www.cgvargas.com.br/single-post/virtualiza%C3%A7%C3%A3o-local-x-computa%C3%A7%C3%A3o-em-nuvem</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Acervo Academico]]></category><pubDate>Fri, 11 Aug 2023 01:57:07 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_535b32e6f4f74f0ba997513e9200720b~mv2.png/v1/fit/w_1000,h_560,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Desvendando a Conexao Entre IMAP, POP3 e a Nuvem: O Poder por Tras dos E-mails na Era Digital]]></title><description><![CDATA[Bem-vindos a um mergulho profundo no coracao da computacao em nuvem e sua interacao magica com os protocolos IMAP e POP3. Preparem-se...]]></description><link>https://www.cgvargas.com.br/single-post/desvendando-a-conex%C3%A3o-entre-imap-pop3-e-a-nuvem-o-poder-por-tr%C3%A1s-dos-e-mails-na-era-digital</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Wed, 09 Aug 2023 21:15:55 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_06c4f785fc9240a784317e62b4c68d94~mv2.png/v1/fit/w_727,h_256,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Entendendo a Nuvem e o Armazenamento Interno: Como Saber Onde Seus Arquivos Estao?]]></title><description><![CDATA[Bem-vindos a um guia descomplicado para entender a diferenca entre a nuvem e o armazenamento interno em seus dispositivos. Se voce ja se...]]></description><link>https://www.cgvargas.com.br/single-post/entendendo-a-nuvem-e-o-armazenamento-interno-como-saber-onde-seus-arquivos-est%C3%A3o</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Dicas]]></category><category><![CDATA[Informacao]]></category><pubDate>Tue, 08 Aug 2023 14:53:24 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_19ba892cfe05407b95a3afc3f8fa241b~mv2.png/v1/fit/w_728,h_367,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Java vs. JavaScript: Comparando Duas Linguagens de Programacao Distintas]]></title><description><![CDATA[Introducao: No mundo da programacao, frequentemente encontramos nomes semelhantes que podem levar a confusoes. Um exemplo disso sao as...]]></description><link>https://www.cgvargas.com.br/single-post/java-vs-javascript-comparando-duas-linguagens-de-programa%C3%A7%C3%A3o-distintas</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><category><![CDATA[Acervo Academico]]></category><pubDate>Sun, 06 Aug 2023 12:50:17 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_0641c141c93a49a9a2d3a071537ed9f0~mv2.jpg/v1/fit/w_810,h_450,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Introducao a Linguagem SQL: O Poder por Tras dos Bancos de Dados]]></title><description><![CDATA[Seja bem-vindo(a) ao nosso blog de tecnologia! Hoje vamos mergulhar no fascinante mundo da linguagem SQL (Structured Query Language). Se...]]></description><link>https://www.cgvargas.com.br/single-post/introdu%C3%A7%C3%A3o-%C3%A0-linguagem-sql-o-poder-por-tr%C3%A1s-dos-bancos-de-dados</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Sat, 05 Aug 2023 01:20:50 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_3651315c8f1b4390b251b4d12d68ac1a~mv2.png/v1/fit/w_1000,h_356,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Introducao ao MongoDB - Um Banco de Dados Nao Relacional]]></title><description><![CDATA[Ola, pessoal! Hoje vamos explorar uma das tecnologias mais populares no mundo dos bancos de dados nao relacionais: o MongoDB. Neste post,...]]></description><link>https://www.cgvargas.com.br/single-post/introdu%C3%A7%C3%A3o-ao-mongodb-um-banco-de-dados-n%C3%A3o-relacional</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Wed, 02 Aug 2023 18:26:43 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_535b32e6f4f74f0ba997513e9200720b~mv2.png/v1/fit/w_1000,h_560,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Desenvolvimento de uma Aplicacao CRUD com Python e PostgreSQL]]></title><description><![CDATA[Ola, pessoal! Hoje vamos explorar um dos conceitos fundamentais no desenvolvimento de aplicacoes web: o CRUD. CRUD e uma sigla que...]]></description><link>https://www.cgvargas.com.br/single-post/desenvolvimento-de-uma-aplica%C3%A7%C3%A3o-crud-com-python-e-postgresql</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Tue, 01 Aug 2023 23:36:09 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_4e243b8e883c4b7091dd0a5a78422de0~mv2.png/v1/fit/w_768,h_406,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[SQL vs. NoSQL: Explorando a Escolha Entre Bancos de Dados Relacionais e Nao Relacionais]]></title><description><![CDATA[Ola, caros leitores! Hoje vamos adentrar no empolgante mundo dos bancos de dados e mergulhar na eterna disputa entre as tecnologias SQL e...]]></description><link>https://www.cgvargas.com.br/single-post/sql-vs-nosql-explorando-a-escolha-entre-bancos-de-dados-relacionais-e-n%C3%A3o-relacionais</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Mon, 31 Jul 2023 14:38:28 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_3e49d93300934dfeb2eb5d7385d514ca~mv2.png/v1/fit/w_747,h_375,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Introducao a Banco de Dados: A Base do Mundo Tecnologico]]></title><description><![CDATA[Bem-vindos ao nosso blog de tecnologia! Hoje, embarcaremos em uma jornada emocionante pelo fascinante mundo dos bancos de dados. Esses...]]></description><link>https://www.cgvargas.com.br/single-post/introdu%C3%A7%C3%A3o-%C3%A0-banco-de-dados-a-base-do-mundo-tecnol%C3%B3gico</link><category><![CDATA[Acervo Academico]]></category><category><![CDATA[Tecnologia]]></category><category><![CDATA[Informacao]]></category><pubDate>Sun, 30 Jul 2023 15:24:26 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_a7e432e04bae4423b45e410dd5d20608~mv2.png/v1/fit/w_600,h_400,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item><item><title><![CDATA[Instalando e Testando o PostgreSQL para Iniciantes]]></title><description><![CDATA[Guia Passo a Passo: Se voce e um estudante iniciante em tecnologia e esta interessado em bancos de dados, o PostgreSQL e uma excelente...]]></description><link>https://www.cgvargas.com.br/single-post/instalando-e-testando-o-postgresql-para-iniciantes</link><category><![CDATA[Tecnologia]]></category><category><![CDATA[Software]]></category><category><![CDATA[Artigo]]></category><category><![CDATA[Informacao]]></category><pubDate>Wed, 26 Jul 2023 18:11:33 GMT</pubDate><enclosure url="https://static.wixstatic.com/media/41a0d9_bee181eb24bf4bd0903d0ad5a36c8261~mv2.jpg/v1/fit/w_610,h_234,al_c,q_80/file.png" length="0" type="image/png"/><dc:creator>Claudio Vargas</dc:creator></item></channel></rss>"""


def upload_imagem(url, public_id):
    if not url or not url.startswith('http'):
        return None
    try:
        print(f"    Upload: {url[:65]}...")
        res = cloudinary.uploader.upload(
            url, folder="cgvargas/blog",
            public_id=public_id, overwrite=False, resource_type="image"
        )
        print(f"    OK -> {res['secure_url']}")
        return res['public_id']
    except Exception as e:
        print(f"    Aviso upload: {e}")
        return None


def slug_unico(titulo):
    base = slugify(titulo)
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
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('cgvargas', 'cgvargas.inf@outlook.com', 'admin123')
    return Autor.objects.create(nome="Claudio Vargas", bio="Fundador da CGVargas Informatica", usuario=user)


def main():
    print("\n" + "="*60)
    print("IMPORTANDO BLOG DO WIX (via RSS) -> DJANGO/SUPABASE")
    print("="*60)

    autor = get_ou_criar_autor()
    print(f"Autor: {autor.nome}\n")

    root = ET.fromstring(RSS_XML)
    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
    items = root.findall('.//item')
    print(f"Encontrados {len(items)} artigos no RSS\n")

    criados = 0
    ignorados = 0

    for i, item in enumerate(items, 1):
        titulo = item.findtext('title', '').strip()
        resumo = item.findtext('description', '').strip()
        link = item.findtext('link', '').strip()
        pub_date_str = item.findtext('pubDate', '')
        enclosure = item.find('enclosure')
        img_url = enclosure.get('url', '') if enclosure is not None else ''

        # extrai apenas a URL base da imagem (sem resize params do wix)
        img_url_base = re.sub(r'/v1/fit/.*$', '', img_url)

        categorias = [c.text for c in item.findall('category') if c.text]
        tags_str = ', '.join(categorias)

        if not titulo:
            ignorados += 1
            continue

        print(f"[{i:02d}] {titulo[:65]}")

        if Post.objects.filter(titulo=titulo).exists():
            print(f"      Ja existe, pulando.")
            ignorados += 1
            continue

        slug = slug_unico(titulo)

        # Data de publicacao
        data_pub = None
        if pub_date_str:
            try:
                data_pub = parsedate_to_datetime(pub_date_str)
            except Exception:
                pass

        # Conteudo: resumo do RSS + link original
        conteudo = (
            f"{resumo}\n\n"
            f"<p><em>Artigo migrado do blog anterior. "
            f"<a href='{link}' target='_blank'>Ver original no Wix</a></em></p>"
        )

        # Upload da imagem
        imagem_id = None
        if img_url_base and img_url_base.startswith('http'):
            imagem_id = upload_imagem(img_url_base, f"cgvargas/blog/{slug}")

        try:
            post = Post(
                titulo=titulo,
                slug=slug,
                resumo=resumo[:500] if resumo else titulo[:200],
                conteudo=conteudo,
                publicado=True,
                autor=autor,
            )
            if data_pub:
                post.criado_em = data_pub
            if imagem_id:
                post.imagem = imagem_id
            post.save()
            criados += 1
            print(f"      Criado: /blog/{slug}/")
        except Exception as e:
            print(f"      ERRO: {e}")
            ignorados += 1

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {criados} posts criados | {ignorados} ignorados")
    print(f"Veja em: http://127.0.0.1:8000/blog/")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
