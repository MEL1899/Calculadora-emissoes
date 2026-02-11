from flask import Flask, render_template, request, send_file
import pandas as pd
from datetime import datetime
import os
from carbon_calculator import (
    calcular_emissao, 
    calcular_fator_idade, 
    calcular_intensidade
)

# Tenta importar configuração do Google Maps API
# Em produção, usa variável de ambiente; em desenvolvimento, usa config.py
import os
try:
    from config import GOOGLE_MAPS_API_KEY
    # Se estiver vazio, tenta variável de ambiente
    if GOOGLE_MAPS_API_KEY == 'YOUR_API_KEY':
        GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY')
except ImportError:
    # Se não houver config.py, usa variável de ambiente
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY')

app = Flask(__name__)

@app.context_processor
def inject_google_maps_key():
    """Injeta a API key do Google Maps em todos os templates"""
    return dict(google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/')
def home():
    return render_template('index.html', ano_atual=datetime.now().year)

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        # 1. Captura todos os dados do formulário
        email = request.form['email']
        tipo_veiculo = request.form.get('tipo_veiculo', 'carro')  # Default para carro
        tipo_combustivel = request.form['tipo_combustivel']
        litros = float(request.form['litros'])
        ano_fabricacao = int(request.form['ano_fabricacao'])
        km_rodado = float(request.form['km_rodado'])
        # Campo de carga é opcional para carros (será 0 se não fornecido)
        carga_ton = float(request.form.get('carga_ton', 0))
        
        # Dados de localização (opcionais)
        endereco_origem = request.form.get('endereco_origem', '')
        endereco_destino = request.form.get('endereco_destino', '')
        lat_origem = request.form.get('lat_origem', '')
        lng_origem = request.form.get('lng_origem', '')
        lat_destino = request.form.get('lat_destino', '')
        lng_destino = request.form.get('lng_destino', '')
        
        # 2. Cria um DataFrame temporário com os dados do formulário
        # Isso permite usar as funções avançadas que esperam DataFrame
        dados_viagem = pd.DataFrame({
            'ID_Viagem': ['WEB_001'],
            'Data': [datetime.now().strftime('%Y-%m-%d')],
            'Frota_ID': ['WEB'],
            'Combustivel_L': [litros],
            'Tipo_Combustivel': [tipo_combustivel],
            'KM_Rodado': [km_rodado],
            'Carga_Ton': [carga_ton],
            'Numero_Eixos': [0],  # Não usado no cálculo, mas necessário para compatibilidade
            'Ano_Fabricacao': [ano_fabricacao]
        })
        
        # 3. Processa usando todas as funções avançadas
        
        # 3.1. Calcula emissão base
        dados_com_emissao = calcular_emissao(dados_viagem)
        
        # 3.2. Calcula fator de idade e emissão final
        dados_com_idade = calcular_fator_idade(dados_com_emissao)
        
        # 3.3. Calcula intensidades e eficiência
        dados_final = calcular_intensidade(dados_com_idade)
        
        # 4. Extrai os resultados para exibição
        resultado = dados_final.iloc[0]  # Primeira (e única) linha
        
        # 5. Gera relatório Excel individual (Resumo em português + Dados técnicos)
        nome_arquivo = f"Relatorio_Carbono_Individual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        caminho_arquivo = os.path.join(os.getcwd(), nome_arquivo)
        
        # Planilha Resumo: relatório legível em português
        resumo = pd.DataFrame({
            'Item': [
                'Tipo de veículo', 'Combustível', 'Litros consumidos (L)', 'Ano de fabricação',
                'Idade do veículo (anos)', 'Quilômetros rodados (km)', 'Emissão base (tCO2e)',
                'Fator de idade', 'Emissão final (tCO2e)', 'Intensidade por km (tCO2e/km)',
                'Eficiência (km/L)', 'E-mail', 'Data do relatório'
            ],
            'Valor': [
                tipo_veiculo_label, tipo_combustivel, f'{litros:.2f}', str(ano_fabricacao),
                str(idade_veiculo), f'{km_rodado:.2f}', f"{resultado['emissao_base']:.4f}",
                f"{resultado['Fator_idade']:.4f}", f"{resultado['emissao_final']:.4f}",
                f"{resultado['Intensidade_tCO2e_por_KM']:.6f}", f"{resultado['Eficiencia_KM_por_L']:.2f}",
                email, datetime.now().strftime('%d/%m/%Y %H:%M')
            ]
        })
        if tipo_veiculo == 'caminhao':
            idx_efic = resumo[resumo['Item'] == 'Eficiência (km/L)'].index[0]
            nova_linha = pd.DataFrame({'Item': ['Carga transportada (toneladas)', 'Intensidade por tonelada (tCO2e/ton)'], 'Valor': [f'{carga_ton:.2f}', f"{resultado['Intensidade_tCO2e_por_Ton']:.6f}"]})
            resumo = pd.concat([resumo.iloc[:idx_efic], nova_linha, resumo.iloc[idx_efic:]]).reset_index(drop=True)
        
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            resumo.to_excel(writer, sheet_name='Resumo', index=False)
            dados_final.to_excel(writer, sheet_name='Dados técnicos', index=False)
        
        # 6. Prepara dados para o template
        ano_atual = datetime.now().year
        idade_veiculo = ano_atual - ano_fabricacao
        
        tipo_veiculo_label = 'Caminhão' if tipo_veiculo == 'caminhao' else 'Carro'
        data_relatorio = datetime.now().strftime('%d/%m/%Y às %H:%M')
        dados_template = {
            'data_relatorio': data_relatorio,
            'email': email,
            'tipo_veiculo': tipo_veiculo_label,
            'tipo_veiculo_raw': tipo_veiculo,
            'tipo_combustivel': tipo_combustivel,
            'litros': f"{litros:.2f}",
            'ano_fabricacao': ano_fabricacao,
            'idade_veiculo': idade_veiculo,
            'km_rodado': f"{km_rodado:.2f}",
            'carga_ton': f"{carga_ton:.2f}",
            'endereco_origem': endereco_origem if endereco_origem else 'Não informado',
            'endereco_destino': endereco_destino if endereco_destino else 'Não informado',
            'emissao_base': f"{resultado['emissao_base']:.4f}",
            'fator_idade': f"{resultado['Fator_idade']:.4f}",
            'emissao_final': f"{resultado['emissao_final']:.4f}",
            'intensidade_ton': f"{resultado['Intensidade_tCO2e_por_Ton']:.6f}",
            'intensidade_km': f"{resultado['Intensidade_tCO2e_por_KM']:.6f}",
            'eficiencia': f"{resultado['Eficiencia_KM_por_L']:.2f}",
            'arquivo_relatorio': f"/download/{nome_arquivo}"
        }
        
        # 7. Renderiza a página de resultado
        return render_template('resultado.html', **dados_template)
        
    except Exception as e:
        # Tratamento de erro
        error_message = f"Erro ao processar o cálculo: {str(e)}"
        return f"<h1>Erro</h1><p>{error_message}</p><a href='/'>Voltar</a>", 400

@app.route('/download/<filename>')
def download_file(filename):
    """Rota para download do relatório Excel"""
    try:
        caminho_arquivo = os.path.join(os.getcwd(), filename)
        if os.path.exists(caminho_arquivo):
            return send_file(caminho_arquivo, as_attachment=True)
        else:
            return "Arquivo não encontrado", 404
    except Exception as e:
        return f"Erro ao fazer download: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)