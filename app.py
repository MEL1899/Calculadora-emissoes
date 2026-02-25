from flask import Flask, render_template, request, send_file
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
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


def _obter_consumo_medio_km_por_litro(tipo_veiculo: str, tipo_combustivel: str) -> float:
    """
    Retorna um consumo médio aproximado (km/L) por tipo de veículo e combustível.
    Valores apenas indicativos para cálculo estimado.
    """
    medias = {
        'carro': {
            'Gasolina': 12.0,
            'Etanol': 8.0,
            'Diesel S10': 14.0,
        },
        'caminhao': {
            'Diesel S10': 2.5,
            'Gasolina': 2.0,
            'Etanol': 1.8,
        }
    }
    tipo = medias.get(tipo_veiculo.lower(), {})
    valor = tipo.get(tipo_combustivel, 5.0)
    return float(valor) if valor > 0 else 5.0


def gerar_relatorio_pdf(dados: dict, caminho_arquivo: str) -> None:
    """Gera um relatório PDF simples e auditável com base nos dados calculados."""
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4, title="Relatório de Emissões - Carbon Log")
    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        spaceAfter=8,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#5a6d67"),
        spaceAfter=12,
    )
    secao_titulo = ParagraphStyle(
        "SecaoTitulo",
        parent=styles["Heading2"],
        fontSize=11,
        textTransform="uppercase",
        textColor=colors.HexColor("#0d5c4a"),
        leading=14,
        spaceAfter=6,
    )
    corpo = styles["Normal"]
    corpo.spaceAfter = 6

    story = []
    story.append(Paragraph("Relatório de Emissões de GEE", titulo))
    story.append(Paragraph(f"Carbon Log — {dados.get('data_relatorio', '')}", subtitulo))
    story.append(Paragraph(f"Emissão total da viagem: <b>{dados.get('emissao_final', '')} tCO2e</b>", corpo))
    story.append(Paragraph(f"Modo de cálculo: {dados.get('modo_calculo_label', '')} ({dados.get('modo_calculo_selo', '')})", corpo))
    story.append(Spacer(1, 12))

    # Dados da viagem
    story.append(Paragraph("Dados da viagem", secao_titulo))
    dados_viagem = [
        ["Tipo de veículo", dados.get("tipo_veiculo")],
        ["Combustível", dados.get("tipo_combustivel")],
        ["Litros consumidos", f"{dados.get('litros', '')} L ({dados.get('litros_texto_origem', '')})"],
        ["Ano de fabricação", dados.get("ano_fabricacao")],
        ["Idade do veículo (anos)", dados.get("idade_veiculo")],
        ["Quilômetros rodados", f"{dados.get('km_rodado', '')} km"],
    ]
    if dados.get("tipo_veiculo_raw") == "caminhao":
        dados_viagem.append(["Carga transportada (t)", dados.get("carga_ton")])

    tabela_viagem = Table(dados_viagem, colWidths=[180, 330])
    tabela_viagem.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#f0f7f5")),
                ("TEXTCOLOR", (0, 0), (1, 0), colors.HexColor("#1a2e28")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d4e5e1")),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#d4e5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(tabela_viagem)
    story.append(Spacer(1, 12))

    # Resultados
    story.append(Paragraph("Resultados do cálculo", secao_titulo))
    dados_resultados = [
        ["Emissão base (tCO2e)", dados.get("emissao_base")],
        ["Fator de idade", dados.get("fator_idade")],
        ["Emissão final (tCO2e)", dados.get("emissao_final")],
        ["Emissão por km (tCO2e/km)", dados.get("intensidade_km")],
        ["Eficiência (km/L)", dados.get("eficiencia")],
    ]
    if dados.get("tipo_veiculo_raw") == "caminhao":
        dados_resultados.append(["Intensidade por tonelada (tCO2e/ton)", dados.get("intensidade_ton")])

    tabela_resultados = Table(dados_resultados, colWidths=[220, 290])
    tabela_resultados.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#f0f7f5")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d4e5e1")),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#d4e5e1")),
            ]
        )
    )
    story.append(tabela_resultados)
    story.append(Spacer(1, 12))

    # Comparação com média do setor
    story.append(Paragraph("Comparação com média do setor", secao_titulo))
    comp_texto = ""
    situacao = dados.get("comparacao_setor_situacao")
    perc = dados.get("comparacao_setor_percentual")
    media_setor = dados.get("media_setor_intensidade_km")
    if situacao == "indisponível":
        comp_texto = "Não foi possível comparar com a média de referência (km ou emissões zeradas)."
    else:
        comp_texto = (
            f"Resultado de aproximadamente {perc}% {situacao} da média de referência "
            f"({media_setor} tCO2e/km)."
        )
    story.append(Paragraph(comp_texto, corpo))
    story.append(Spacer(1, 12))

    # Nota ESG / GHG Protocol
    story.append(
        Paragraph(
            "Empresas que precisam reportar emissões ao GHG Protocol ou clientes ESG exigentes "
            "utilizam relatórios auditáveis.",
            corpo,
        )
    )

    doc.build(story)


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
        modo_calculo = request.form.get('modo_calculo', 'estimado')
        ano_fabricacao = int(request.form['ano_fabricacao'])
        km_rodado = float(request.form.get('km_rodado', 0) or 0)
        # Campo de carga é opcional para carros (será 0 se não fornecido)
        carga_ton = float(request.form.get('carga_ton', 0) or 0)

        # Define litros conforme o modo de cálculo
        litros_estimado = False
        if modo_calculo == 'preciso':
            litros = float(request.form['litros'])
        else:
            # Estimativa de litros com base em km rodado e consumo médio
            consumo_medio = _obter_consumo_medio_km_por_litro(tipo_veiculo, tipo_combustivel)
            if km_rodado <= 0 or consumo_medio <= 0:
                litros = 0.0
            else:
                litros = km_rodado / consumo_medio
            litros_estimado = True
        
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
        ano_atual = datetime.now().year
        idade_veiculo = ano_atual - ano_fabricacao
        tipo_veiculo_label = 'Caminhão' if tipo_veiculo == 'caminhao' else 'Carro'
        modo_calculo_label = 'Modo preciso' if modo_calculo == 'preciso' else 'Modo estimado'
        modo_calculo_selo = 'Alta precisão' if modo_calculo == 'preciso' else 'Resultado estimado (consumo médio)'
        litros_texto_origem = 'informados pelo usuário' if not litros_estimado else 'estimados a partir dos km rodados'

        # Comparação com média de intensidade do setor (valor fixo simulado)
        media_setor_intensidade_km = 0.0008  # tCO2e/km (valor de referência fixo)
        intensidade_km_valor = float(resultado['Intensidade_tCO2e_por_KM'])
        if km_rodado > 0 and intensidade_km_valor > 0 and media_setor_intensidade_km > 0:
            diff_percent = (intensidade_km_valor - media_setor_intensidade_km) / media_setor_intensidade_km * 100
            if diff_percent > 5:
                situacao_setor = 'acima'
            elif diff_percent < -5:
                situacao_setor = 'abaixo'
            else:
                situacao_setor = 'na faixa da'
            diff_percent_formatado = f"{abs(diff_percent):.1f}"
        else:
            situacao_setor = 'indisponível'
            diff_percent_formatado = None
        
        # 5. Gera nome e caminho do relatório PDF (relatório auditável)
        agora = datetime.now()
        nome_arquivo = f"Relatorio_Carbono_Individual_{agora.strftime('%Y%m%d_%H%M%S')}.pdf"
        caminho_arquivo = os.path.join(os.getcwd(), nome_arquivo)
        
        # 6. Prepara dados para o template
        data_relatorio = agora.strftime('%d/%m/%Y às %H:%M')
        dados_template = {
            'data_relatorio': data_relatorio,
            'modo_calculo': modo_calculo,
            'modo_calculo_label': modo_calculo_label,
            'modo_calculo_selo': modo_calculo_selo,
            'litros_estimado': litros_estimado,
            'litros_texto_origem': litros_texto_origem,
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
            'media_setor_intensidade_km': f"{media_setor_intensidade_km:.6f}",
            'comparacao_setor_percentual': diff_percent_formatado,
            'comparacao_setor_situacao': situacao_setor,
            'arquivo_relatorio': f"/download/{nome_arquivo}"
        }

        # 7. Gera o PDF baseado nesses dados
        gerar_relatorio_pdf(dados_template, caminho_arquivo)
        
        # 8. Renderiza a página de resultado
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