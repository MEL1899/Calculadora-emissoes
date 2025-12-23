# 🗺️ Como Obter a Chave da API do Google Maps

Para usar o mapa integrado no formulário, você precisa de uma chave de API do Google Maps.

## 📋 Passo a Passo

### 1. **Criar uma Conta no Google Cloud Platform**

1. Acesse: https://console.cloud.google.com/
2. Faça login com sua conta Google
3. Aceite os termos de serviço se solicitado

### 2. **Criar um Novo Projeto**

1. No topo da página, clique no seletor de projetos
2. Clique em **"Novo Projeto"**
3. Dê um nome ao projeto (ex: "Carbon Log Maps")
4. Clique em **"Criar"**

### 3. **Habilitar as APIs Necessárias**

1. No menu lateral, vá em **"APIs e Serviços" > "Biblioteca"**
2. Procure e habilite as seguintes APIs:
   - **Maps JavaScript API** (obrigatória)
   - **Places API** (para autocomplete de endereços e estabelecimentos)
   - **Geocoding API** (para buscar coordenadas de endereços)
   - **Directions API** (para calcular distância de estrada) ⭐ **NOVA - OBRIGATÓRIA**
   - **Geometry Library** (já incluída na Maps JavaScript API)

### 4. **Criar Credenciais (API Key)**

1. Vá em **"APIs e Serviços" > "Credenciais"**
2. Clique em **"Criar Credenciais" > "Chave de API"**
3. Sua chave será criada e exibida
4. **Copie a chave** (ela será algo como: `AIzaSyC...`)

### 5. **Restringir a Chave (Recomendado por Segurança)**

1. Clique na chave recém-criada para editá-la
2. Em **"Restrições de aplicativo"**, escolha **"Referenciadores de HTTP"**
3. Adicione as URLs onde seu site será acessado:
   - `http://localhost:*` (para desenvolvimento)
   - `http://127.0.0.1:*` (para desenvolvimento)
   - `https://seudominio.com/*` (para produção)
4. Em **"Restrições de API"**, selecione:
   - Maps JavaScript API
   - Places API
   - Geocoding API
   - Directions API ⭐ **NOVA - Para calcular distância de estrada**
5. Clique em **"Salvar"**

### 6. **Configurar no Projeto**

1. Abra o arquivo `config.py`
2. Substitua `'YOUR_API_KEY'` pela sua chave:

```python
GOOGLE_MAPS_API_KEY = 'AIzaSyC...sua_chave_aqui'
```

## 💰 **Sobre Custos**

- **Gratuito até $200/mês** (créditos mensais)
- Isso permite aproximadamente:
  - 28.000 carregamentos de mapas
  - 100.000 requisições de autocomplete
  - 40.000 requisições de geocodificação
  - 40.000 requisições de direções (rotas)

Para uso pessoal/pequenos projetos, geralmente fica dentro do limite gratuito.

## ⚠️ **Importante**

- **NUNCA** commite a chave da API no Git sem restrições
- Adicione `config.py` ao `.gitignore` se for compartilhar o código
- Use restrições de API para evitar uso indevido

## 🔧 **Testar**

1. Configure a chave no `config.py`
2. Execute `python app.py`
3. Acesse `http://localhost:5000`
4. O mapa deve aparecer no formulário

## 🆘 **Problemas Comuns**

### "This page can't load Google Maps correctly"
- Verifique se a API key está correta
- Verifique se as APIs necessárias estão habilitadas
- Verifique se não há restrições bloqueando sua requisição

### Autocomplete não funciona
- Certifique-se de que a **Places API** está habilitada
- Agora aceita estabelecimentos e locais, não apenas endereços

### Distância calculada em linha reta ao invés de estrada
- Certifique-se de que a **Directions API** está habilitada
- Esta API é necessária para calcular a distância real de estrada

### Mapa aparece mas não permite interação
- Verifique se a **Maps JavaScript API** está habilitada e a chave está correta

