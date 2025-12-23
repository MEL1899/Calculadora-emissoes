# 🌱 Carbon Log - Calculadora de Emissões GEE

Projeto de Engenharia Ambiental - USP São Carlos

## 📋 Descrição

Sistema web para cálculo de emissões de gases de efeito estufa (GEE) com integração Google Maps para cálculo de distâncias de estrada.

## 🚀 Como Rodar

Veja o guia completo em: **[COMO_RODAR.md](COMO_RODAR.md)**

**Resumo rápido:**
1. `pip install -r requirements.txt`
2. `python app.py`
3. Acesse: http://localhost:5000

## 🗺️ Configurar Google Maps (Opcional)

Para usar a funcionalidade de mapas e autocomplete de endereços:
1. Veja: **[COMO_OBTER_API_KEY_GOOGLE_MAPS.md](COMO_OBTER_API_KEY_GOOGLE_MAPS.md)**
2. Copie `config.example.py` para `config.py`
3. Configure sua API key

## 📁 Estrutura do Projeto

- `app.py` - Aplicação Flask principal
- `carbon_calculator.py` - Funções de cálculo de emissões
- `config.py` - Configuração da API key do Google Maps
- `templates/` - Templates HTML
- `dados_mantram.csv` - Dados de exemplo

## ⚙️ Funcionalidades

- ✅ Cálculo de emissões base por tipo de combustível
- ✅ Ajuste por idade do veículo
- ✅ Cálculo de intensidade de emissões
- ✅ Integração com Google Maps
- ✅ Autocomplete de endereços e estabelecimentos
- ✅ Cálculo automático de distância de estrada
- ✅ Geração de relatório Excel

## 📝 Requisitos

- Python 3.7+
- Flask
- pandas
- openpyxl
- Google Maps API Key (opcional, para funcionalidade de mapas)

