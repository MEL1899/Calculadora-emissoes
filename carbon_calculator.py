import pandas as pd
from datetime import datetime

def carregar_dados():
    """
    Carrega o arquivo 'dados_exemplo.csv' no formato UTF-8 e retorna o DataFrame.
    
    Returns:
        pandas.DataFrame: DataFrame com os dados do arquivo CSV
    """
    try:
        # Carrega o arquivo CSV com encoding UTF-8
        df = pd.read_csv('dados_exemplo.csv', encoding='utf-8')
        
        return df
    
    except FileNotFoundError:
        print("Erro: Arquivo 'dados_exemplo.csv' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None

# --- MÓDULO B: Fatores de Emissão (Constantes Técnicas) ---
def definir_fatores_emissao():
    """
    Define os fatores de emissão padronizados (GHG Protocol Brasil) em tCO2e/L.
    """
    # Fatores baseados em referências como GHG Protocol Brasil (adaptado para fins didáticos)
    fatores = {
        'Diesel S10': 0.002671,  # 2.671 kg CO2e por Litro de Diesel
        'Gasolina': 0.00232,    # Exemplo: 2.32 kg CO2e por Litro de Gasolina
        'Etanol': 0.00067,      # Exemplo: 0.67 kg CO2e por Litro de Etanol
    }
    return fatores

def calcular_emissao(df, tipo_combustivel=None):
    """
    Calcula as emissões totais (em tCO2e) por viagem usando o consumo de combustível.
    
    Aceita dois tipos de entrada:
    - DataFrame: Processa em lote usando as colunas 'Tipo_Combustivel' e 'Combustivel_L'
    - Número (int/float): Calcula emissão individual. Requer o parâmetro 'tipo_combustivel'
    
    Args:
        df: DataFrame com colunas 'Tipo_Combustivel' e 'Combustivel_L', ou um número (int/float)
        tipo_combustivel (str, opcional): Tipo de combustível necessário quando 'df' é um número.
                                         Deve ser 'Diesel S10', 'Gasolina' ou 'Etanol'
    
    Returns:
        DataFrame: Se a entrada for DataFrame, retorna DataFrame com colunas adicionais
        float: Se a entrada for número, retorna a emissão calculada em tCO2e
    """
    # 1. Obter os fatores de emissão
    fatores_emissao = definir_fatores_emissao()
    
    # 2. Verificar se a entrada é um número (int ou float)
    if isinstance(df, (int, float)):
        # Modo de cálculo individual
        if tipo_combustivel is None:
            raise ValueError("Para cálculo individual, é necessário informar o 'tipo_combustivel'")
        
        # Verificar se o tipo de combustível existe nos fatores
        if tipo_combustivel not in fatores_emissao:
            raise ValueError(f"Tipo de combustível '{tipo_combustivel}' não encontrado. "
                           f"Tipos disponíveis: {list(fatores_emissao.keys())}")
        
        # Calcular emissão individual: Emissão Base = Litros * Fator_Combustível
        fator = fatores_emissao[tipo_combustivel]
        emissao_base = df * fator
        
        return emissao_base
    
    # 3. Modo DataFrame: Processamento em lote (lógica original)
    elif isinstance(df, pd.DataFrame):
        # Mapear o Fator de Emissão para cada linha do DataFrame
        df['Fator_Emissao'] = df['Tipo_Combustivel'].map(fatores_emissao)
        
        # Aplicar a fórmula fundamental: Emissão Base = Litros * Fator_Combustível
        df['emissao_base'] = df['Combustivel_L'] * df['Fator_Emissao']
        
        # Tratar casos onde o tipo de combustível não foi encontrado
        df['emissao_base'] = df['emissao_base'].fillna(0) 
        
        return df
    
    else:
        raise TypeError(f"Tipo de entrada não suportado: {type(df)}. "
                       f"Esperado: DataFrame, int ou float")


def calcular_fator_idade(df):
    """
    Calcula o fator de idade do veículo usando penalidade progressiva por blocos de ano de fabricação.
    Também calcula a idade do veículo e emissões finais.
    
    Taxa de Penalidade Anual por blocos:
    - 1.0% se >= 2023
    - 1.5% se >= 2012 e < 2023  
    - 2.5% se >= 2006 e < 2012
    - 3.0% se >= 2000 e < 2006
    - 4.0% se >= 1996 e < 2000
    - 5.0% se < 1996
    
    Fórmula: FA = 1.0 + (Ano Atual - Ano Fabricação) × Taxa de Penalidade
    """
    ano_atual = datetime.now().year
    
    def calcular_taxa_penalidade(ano_fabricacao):
        """Calcula a taxa de penalidade anual baseada no ano de fabricação."""
        if ano_fabricacao >= 2023:
            return 0.01  # 1.0%
        elif ano_fabricacao >= 2012:
            return 0.015  # 1.5%
        elif ano_fabricacao >= 2006:
            return 0.025  # 2.5%
        elif ano_fabricacao >= 2000:
            return 0.03   # 3.0%
        elif ano_fabricacao >= 1996:
            return 0.04   # 4.0%
        else:
            return 0.05   # 5.0%
    
    def calcular_fator_ajuste(row):
        """Calcula o Fator de Ajuste de Idade (FA) para cada veículo."""
        ano_fabricacao = row['Ano_Fabricacao']
        idade_veiculo = ano_atual - ano_fabricacao
        taxa_penalidade = calcular_taxa_penalidade(ano_fabricacao)
        
        fator_ajuste = 1.0 + idade_veiculo * taxa_penalidade
        return fator_ajuste
    
    # Calcula idade do veículo
    df['Idade_Veiculo'] = ano_atual - df['Ano_Fabricacao']
    df['Idade_Veiculo'] = df['Idade_Veiculo'].clip(lower=0)
    
    # Aplica o cálculo para cada linha
    df['Fator_idade'] = df.apply(calcular_fator_ajuste, axis=1)
    
    # Calcula emissao_final = fator_idade * emissao_base
    df['emissao_final'] = df['Fator_idade'] * df['emissao_base']
    
    return df

def calcular_intensidade(df):
    """
    Calcula a intensidade de emissões (tCO2e por tonelada e por km) e eficiência de combustível.
    Trata divisão por zero retornando 0 quando Carga_Ton ou KM_Rodado for zero.
    """
    # Calcula a intensidade por tonelada
    df['Intensidade_tCO2e_por_Ton'] = df.apply(
        lambda row: 0 if row['Carga_Ton'] == 0 else row['emissao_final'] / row['Carga_Ton'], 
        axis=1
    )
    
    # Calcula a intensidade por km rodado
    df['Intensidade_tCO2e_por_KM'] = df.apply(
        lambda row: 0 if row['KM_Rodado'] == 0 else row['emissao_final'] / row['KM_Rodado'], 
        axis=1
    )
    
    # Calcula eficiência de combustível (km por litro)
    df['Eficiencia_KM_por_L'] = df.apply(
        lambda row: 0 if row['Combustivel_L'] == 0 else row['KM_Rodado'] / row['Combustivel_L'], 
        axis=1
    )
    
    return df

def gerar_relatorio_excel(df):
    """
    Gera um relatório em Excel com o DataFrame final (emissões base, final, fator idade e intensidade).
    Salva o arquivo como 'Relatorio_Carbono_Frota.xlsx' sem incluir o índice das linhas.
    """
    try:
        # Salva o DataFrame em Excel sem o índice
        df.to_excel('Relatorio_Carbono_Frota.xlsx', index=False)
        print(f"\nRelatório salvo com sucesso: Relatorio_Carbono_Frota.xlsx")
        print(f"Arquivo contém {df.shape[0]} linhas e {df.shape[1]} colunas")
        
    except Exception as e:
        print(f"Erro ao salvar o relatório Excel: {e}")

# Exemplo de uso da função
if __name__ == "__main__":
    # Carrega os dados
    dados = carregar_dados()
    
    if dados is not None:
        print(f"\nDataFrame carregado com sucesso!")
        print(f"Dimensões: {dados.shape[0]} linhas e {dados.shape[1]} colunas")
        
        # 1. CHAMA a função para calcular as emissões base
        dados_com_emissao_base = calcular_emissao(dados)

        # 2. CHAMA a função para calcular o fator de idade, idade, emissao_final e razão
        dados_com_fator_idade = calcular_fator_idade(dados_com_emissao_base)

        # 3. CHAMA a função para calcular as intensidades (por tonelada e por km)
        dados_final = calcular_intensidade(dados_com_fator_idade)

        # 4. IMPRIME os resultados do cálculo
        print("\n--- Resultados do Cálculo de Carbono ---")
        print(dados_final[['Frota_ID', 'Numero_Eixos', 'Ano_Fabricacao', 'Idade_Veiculo', 'Fator_idade', 'emissao_base', 'emissao_final', 'Intensidade_tCO2e_por_Ton', 'Intensidade_tCO2e_por_KM', 'Eficiencia_KM_por_L']])

        # 5. Calcula e imprime a emissão TOTAL (base e final)
        emissao_base_total = dados_final['emissao_base'].sum()
        emissao_final_total = dados_final['emissao_final'].sum()
        print(f"\nEmissão BASE TOTAL (tCO2e): {emissao_base_total:.3f} toneladas")
        print(f"Emissão FINAL TOTAL (tCO2e): {emissao_final_total:.3f} toneladas")
        
        # 6. Gera o relatório em Excel
        gerar_relatorio_excel(dados_final)