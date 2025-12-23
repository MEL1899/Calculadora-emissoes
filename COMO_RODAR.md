# 🚀 COMO RODAR O PROJETO CARBON LOG

## 📋 Pré-requisitos

- Python 3.7 ou superior instalado
- pip (geralmente já vem com Python)

## 🔧 Passo 1: Instalar Dependências

Abra o terminal/PowerShell na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

Isso irá instalar:
- **Flask** - Framework web
- **pandas** - Manipulação de dados
- **openpyxl** - Para gerar arquivos Excel

## ▶️ Passo 2: Executar o Programa

Execute o comando:

```bash
python app.py
```

Você verá uma mensagem similar a:

```
 * Running on http://127.0.0.1:5000
 * Running on http://[::]:5000
Press CTRL+C to quit
```

## 🌐 Passo 3: Acessar o Site

Abra seu navegador e acesse:

```
http://localhost:5000
```

ou

```
http://127.0.0.1:5000
```

## 📝 Passo 4: Usar a Calculadora

1. Preencha todos os campos do formulário:
   - E-mail
   - Tipo de combustível
   - Quantidade de litros
   - Ano de fabricação do veículo
   - Quilômetros rodados
   - Carga transportada (toneladas)

2. Clique em "📊 Calcular e Gerar Relatório Completo"

3. Veja os resultados na página formatada

4. Baixe o relatório Excel gerado

## 🛑 Para Parar o Servidor

Pressione `CTRL + C` no terminal onde o servidor está rodando.

## ⚠️ Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'flask'"
**Solução:** Execute `pip install -r requirements.txt`

### Erro: "ModuleNotFoundError: No module named 'openpyxl'"
**Solução:** Execute `pip install openpyxl` ou `pip install -r requirements.txt`

### Porta 5000 já em uso
**Solução:** Altere a última linha do `app.py` de:
```python
app.run(debug=True)
```
para:
```python
app.run(debug=True, port=5001)
```
E acesse `http://localhost:5001`

### Erro ao gerar Excel
**Solução:** Certifique-se de que a pasta tem permissão de escrita e que o openpyxl está instalado.

