import pandas as pd

# Carrega os dados
df = pd.read_csv('dados_mantram.csv')

print('=== ANALISE DE CONSUMO ===')
df['Consumo_L_por_100km'] = (df['Combustivel_L'] / df['KM_Rodado']) * 100

print('Consumo medio por 100km por numero de eixos:')
print(df.groupby('Numero_Eixos')['Consumo_L_por_100km'].mean())

print('\n=== MULTIPLAS VIAGENS ===')
print('Veiculos com mais de 1 viagem:')
viagens_por_veiculo = df['Frota_ID'].value_counts()
print(viagens_por_veiculo.head(10))

print('\n=== ANALISE DETALHADA ===')
print('Top 5 piores consumos:')
worst = df.nlargest(5, 'Consumo_L_por_100km')[['Frota_ID', 'Combustivel_L', 'KM_Rodado', 'Consumo_L_por_100km']]
print(worst)

print('\nTop 5 melhores consumos:')
best = df.nsmallest(5, 'Consumo_L_por_100km')[['Frota_ID', 'Combustivel_L', 'KM_Rodado', 'Consumo_L_por_100km']]
print(best)

print('\n=== ESTATISTICAS GERAIS ===')
print(f'Consumo medio geral: {df["Consumo_L_por_100km"].mean():.2f} L/100km')
print(f'Consumo minimo: {df["Consumo_L_por_100km"].min():.2f} L/100km')
print(f'Consumo maximo: {df["Consumo_L_por_100km"].max():.2f} L/100km')
