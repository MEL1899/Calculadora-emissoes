# 🚀 Guia de Deploy Gratuito - Carbon Log

## ✅ Status Atual

Seu projeto **JÁ está conectado ao GitHub**! 
- Branch: `main`
- Remote: `origin/main`

## 📤 Passo 1: Fazer Commit das Mudanças

Antes de fazer deploy, salve as mudanças no GitHub:

```bash
# Adicionar todos os arquivos novos e modificados
git add .

# Fazer commit
git commit -m "Atualização: integração Google Maps e funcionalidades avançadas"

# Enviar para GitHub
git push origin main
```

## 🌐 Opções de Deploy Gratuito

### Opção 1: **Render.com** ⭐ (Recomendado - Mais Fácil)

**Vantagens:**
- ✅ Totalmente gratuito
- ✅ Deploy automático do GitHub
- ✅ HTTPS automático
- ✅ Muito fácil de configurar

**Passos:**

1. **Criar conta:**
   - Acesse: https://render.com
   - Faça login com GitHub

2. **Criar novo serviço:**
   - Clique em "New +" > "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o repositório "Projeto Carbon Log"

3. **Configurar:**
   - **Name:** `carbon-log` (ou o nome que preferir)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

4. **Variáveis de Ambiente:**
   - Vá em "Environment"
   - Adicione: `GOOGLE_MAPS_API_KEY` = sua chave da API

5. **Deploy:**
   - Clique em "Create Web Service"
   - Aguarde o deploy (2-3 minutos)
   - Pronto! Seu site estará online em: `https://carbon-log.onrender.com`

**⚠️ Importante:**
- Instale gunicorn: `pip install gunicorn`
- Adicione ao `requirements.txt`: `gunicorn==21.2.0`

---

### Opção 2: **PythonAnywhere** (Muito Simples)

**Vantagens:**
- ✅ Gratuito para sites básicos
- ✅ Interface web completa
- ✅ Fácil de usar

**Passos:**

1. **Criar conta:**
   - Acesse: https://www.pythonanywhere.com
   - Crie conta gratuita

2. **Upload dos arquivos:**
   - Vá em "Files"
   - Faça upload de todos os arquivos do projeto
   - OU conecte com GitHub (mais fácil)

3. **Configurar Web App:**
   - Vá em "Web"
   - Clique em "Add a new web app"
   - Escolha Flask
   - Selecione Python 3.10
   - Configure o caminho do arquivo: `/home/seuusuario/mysite/app.py`

4. **Configurar variáveis:**
   - Em "Web" > "Static files"
   - Configure se necessário
   - Em "Web" > "Environment variables"
   - Adicione: `GOOGLE_MAPS_API_KEY`

5. **Reload:**
   - Clique em "Reload"
   - Acesse: `https://seuusuario.pythonanywhere.com`

---

### Opção 3: **Railway** (Moderno)

**Vantagens:**
- ✅ Gratuito (com créditos mensais)
- ✅ Deploy automático
- ✅ Muito moderno

**Passos:**

1. Acesse: https://railway.app
2. Login com GitHub
3. "New Project" > "Deploy from GitHub repo"
4. Selecione seu repositório
5. Railway detecta automaticamente que é Flask
6. Adicione variável de ambiente: `GOOGLE_MAPS_API_KEY`
7. Deploy automático!

---

### Opção 4: **Fly.io** (Para Apps Mais Complexos)

**Vantagens:**
- ✅ Gratuito com limites generosos
- ✅ Muito rápido
- ✅ Global CDN

**Passos:**

1. Instale Fly CLI: `iwr https://fly.io/install.ps1 -useb | iex`
2. Login: `fly auth login`
3. No diretório do projeto: `fly launch`
4. Siga as instruções
5. Configure variáveis: `fly secrets set GOOGLE_MAPS_API_KEY=sua_chave`

---

## 🔧 Preparação para Deploy

### 1. Atualizar requirements.txt

Adicione `gunicorn` para produção:

```txt
Flask==3.0.0
pandas==2.1.3
openpyxl==3.1.2
gunicorn==21.2.0
```

### 2. Modificar app.py para Produção

Altere a última linha de:
```python
app.run(debug=True)
```

Para:
```python
if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(debug=True)
    # Para produção, o gunicorn será usado
```

### 3. Usar Variáveis de Ambiente

Modifique `app.py` para ler de variáveis de ambiente:

```python
import os

# Tenta importar configuração do Google Maps API
try:
    from config import GOOGLE_MAPS_API_KEY
except ImportError:
    # Em produção, usa variável de ambiente
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY')
```

### 4. Atualizar Restrições da API Key

No Google Cloud Console, adicione seu domínio de produção:
- `https://seu-app.onrender.com/*`
- `https://seuusuario.pythonanywhere.com/*`
- etc.

---

## 📋 Checklist Antes do Deploy

- [ ] Fazer commit e push no GitHub
- [ ] Adicionar `gunicorn` ao `requirements.txt`
- [ ] Configurar variáveis de ambiente no serviço
- [ ] Atualizar restrições da API key do Google Maps
- [ ] Testar localmente antes de fazer deploy

---

## 🎯 Recomendação Final

**Para começar rápido:** Use **Render.com**
- Mais fácil
- Deploy automático
- HTTPS gratuito
- Suporte a Flask nativo

**Quer ajuda com algum passo específico?** Posso ajudar a configurar!

