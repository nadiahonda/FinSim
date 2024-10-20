import streamlit as st
import numpy as np
import locale
import pandas as pd

# Configurar o locale para o formato brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para formatar valores monetários
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True)

# Função para converter entrada de texto formatada para float
def converter_para_float(valor_texto):
    try:
        valor_texto = valor_texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(valor_texto)
    except ValueError:
        return 0.0

# Função para calcular o CET de um financiamento
def calcular_cet_financiamento(valor_total, entrada, taxa_juros, meses):
    saldo_devedor = valor_total - entrada
    if taxa_juros == 0:
        parcela = saldo_devedor / meses
    else:
        parcela = saldo_devedor * (taxa_juros * (1 + taxa_juros)**meses) / ((1 + taxa_juros)**meses - 1)
    
    cet_financiamento = parcela * meses + entrada
    return cet_financiamento, parcela

# Função para calcular saldo final com tesouro selic, aplicando juros compostos e subtraindo parcelas
def calcular_saldo_investido(valor_investido, taxa_selic_mensal, meses, parcela=None):
    saldo = valor_investido
    saldos_mensais = []
    for i in range(meses):
        rendimento_mensal = saldo * taxa_selic_mensal
        saldo += rendimento_mensal
        if parcela:
            saldo -= parcela
        saldos_mensais.append(saldo)
    return saldo, saldos_mensais

# Inputs do usuário
st.title('Simulador')

# Inputs formatados
valor_total_input = st.text_input('Valor total da compra', value=formatar_moeda(140000.0))
valor_entrada_input = st.text_input('Valor de entrada do financiamento', value=formatar_moeda(70000.0))

# Conversão para float
valor_total = converter_para_float(valor_total_input)
valor_entrada = converter_para_float(valor_entrada_input)

taxa_juros_input = st.text_input('Taxa de juros do financiamento (% mensal)', value="0,0")
taxa_juros = converter_para_float(taxa_juros_input) / 100

meses = st.number_input('Número de meses do financiamento', min_value=1, value=36)

desconto_vista_input = st.text_input('Desconto para compra à vista (%)', value="10,0")
desconto_vista = converter_para_float(desconto_vista_input) / 100

taxa_selic_input = st.text_input('Rendimento Anual (%)', value="10,0")
taxa_selic = converter_para_float(taxa_selic_input) / 100

# Convertendo taxa Selic anual para mensal composta
taxa_selic_mensal = (1 + taxa_selic) ** (1 / 12) - 1

# Cálculos para compra à vista
valor_vista = valor_total * (1 - desconto_vista)
cet_vista = valor_vista  # O CET da compra à vista é o próprio valor pago à vista
saldo_final_vista, saldos_mensais_vista = calcular_saldo_investido(valor_total - valor_vista, taxa_selic_mensal, meses)

# Cálculos para financiamento
cet_financiamento, parcela = calcular_cet_financiamento(valor_total, valor_entrada, taxa_juros, meses)
saldo_inicial_financiamento = valor_total - valor_entrada
saldo_final_financiamento, saldos_mensais_financiamento = calcular_saldo_investido(saldo_inicial_financiamento, taxa_selic_mensal, meses, parcela)

# Preparar os dados para a tabela de comparação
dados_comparacao = {
    "Cenário": ["Compra à Vista", "Financiamento"],
    "CET Total": [formatar_moeda(cet_vista), formatar_moeda(cet_financiamento)],
    "Saldo": [formatar_moeda(saldo_final_vista), formatar_moeda(saldo_final_financiamento)]
}

# Criar um DataFrame para exibir como tabela
df_comparacao = pd.DataFrame(dados_comparacao)

# Exibir os resultados em uma tabela interativa sem índice
st.subheader('Comparação dos Cenários')
st.dataframe(df_comparacao.reset_index(drop=True))

# Análise do resultado
if saldo_final_vista > saldo_final_financiamento:
    resultado = 'Compra à vista é mais vantajosa.'
else:
    resultado = 'Financiamento é mais vantajoso.'

st.write(resultado)

# Preparar os dados para a tabela de saldos mensais
dados_mensais = {
    "Saldo - Compra à Vista": [formatar_moeda(saldo) for saldo in saldos_mensais_vista],
    "Saldo - Financiamento": [formatar_moeda(saldo) for saldo in saldos_mensais_financiamento]
}

# Criar um DataFrame para exibir como tabela de saldos mensais
df_mensais = pd.DataFrame(dados_mensais)

# Exibir a tabela de saldos mensais sem índice
st.subheader('Saldos Mensais')
st.dataframe(df_mensais)
