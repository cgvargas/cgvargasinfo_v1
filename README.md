# CGVargas Informática — Site Institucional

Site oficial da **CGVargas Informática**, desenvolvido em Django 6.x como migração do Wix para uma solução própria, moderna e sem custos mensais de plataforma.

## 🚀 Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Framework | Django 6.x |
| Banco de Dados | PostgreSQL (Supabase) |
| Imagens | Cloudinary |
| Assets Estáticos | WhiteNoise |
| Deploy | Render.com |
| Servidor | Gunicorn |

## 📄 Páginas

- **/** — Home com hero animado, serviços, portfólio e blog
- **/sobre/** — Sobre a empresa
- **/servicos/** — Software & Desenvolvimento
- **/hardware/** — Hardware & Manutenção
- **/portfolio/** — Portfólio de projetos
- **/blog/** — CGTecnoBlog
- **/glossario/** — Glossário de TI
- **/contato/** — Formulário de contato
- **/admin/** — Painel administrativo
- **/ping/** — Health check (UptimeRobot keep-alive)

## ⚙️ Configuração Local

```bash
# 1. Clonar o repositório
git clone https://github.com/cgvargas/cgvargasinfo_v1.git
cd cgvargasinfo_v1

# 2. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 5. Rodar migrations
python manage.py migrate

# 6. Criar superusuário
python manage.py createsuperuser

# 7. Rodar servidor
python manage.py runserver
```

## 🔑 Variáveis de Ambiente (.env)

```
SECRET_KEY=sua-secret-key
DEBUG=True
DATABASE_URL=postgresql://...  # Supabase connection string
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

## 🌐 Deploy — Render.com

1. Faça fork/push para o GitHub
2. Crie um **Web Service** no Render apontando para este repositório
3. Configure as variáveis de ambiente no painel do Render
4. O `render.yaml` e `build.sh` cuidam do resto automaticamente

## 📡 Keep-Alive — UptimeRobot

Configure um monitor HTTP no [UptimeRobot](https://uptimerobot.com) apontando para `/ping/` a cada 5 minutos para manter Render e Supabase sempre ativos.

## 📝 Licença

© CGVargas Informática 2017–2025. Todos os direitos reservados.
