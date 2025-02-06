import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def pegar_dados_yahoo(codigo, periodo):
    dados = yf.download(codigo, period=periodo, interval="15m")
    dados = dados[['Close', 'Volume']]
    dados.rename(columns={'Close': 'fechamento', 'Volume': 'volume'}, inplace=True)
    return dados

def calcular_indicadores(dados):
    dados['media_rapida'] = dados['fechamento'].rolling(window=7).mean()
    dados['media_devagar'] = dados['fechamento'].rolling(window=40).mean()
    dados['ema_14'] = dados['fechamento'].ewm(span=14, adjust=False).mean()
    delta = dados['fechamento'].diff(1)
    ganho = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganho / perda
    dados['rsi'] = 100 - (100 / (1 + rs))
    dados['stddev'] = dados['fechamento'].rolling(window=20).std()
    dados['bollinger_sup'] = dados['media_rapida'] + (dados['stddev'] * 2)
    dados['bollinger_inf'] = dados['media_rapida'] - (dados['stddev'] * 2)
    dados['retorno'] = dados['fechamento'].pct_change()
    dados['retorno_acumulado'] = (1 + dados['retorno']).cumprod()
    dados['macd'] = dados['fechamento'].ewm(span=12, adjust=False).mean() - dados['fechamento'].ewm(span=26, adjust=False).mean()
    dados['sinal_macd'] = dados['macd'].ewm(span=9, adjust=False).mean()
    return dados

def gerar_graficos(dados):
    plt.figure(figsize=(12, 6))
    plt.plot(dados.index, dados['fechamento'], label='Preço de Fechamento', color='blue')
    plt.plot(dados.index, dados['media_rapida'], label='Média Rápida (7 períodos)', color='orange')
    plt.plot(dados.index, dados['media_devagar'], label='Média Lenta (40 períodos)', color='green')
    plt.fill_between(dados.index, dados['bollinger_sup'], dados['bollinger_inf'], color='gray', alpha=0.2, label='Bandas de Bollinger')
    plt.title('Análise Técnica de Solana (SOL)')
    plt.legend()
    plt.savefig('grafico_estrategia.png')
    plt.close()
    
    plt.figure(figsize=(12, 4))
    plt.plot(dados.index, dados['rsi'], label='RSI (14 períodos)', color='purple')
    plt.axhline(70, linestyle='--', color='red', alpha=0.5)
    plt.axhline(30, linestyle='--', color='green', alpha=0.5)
    plt.title('Índice de Força Relativa (RSI)')
    plt.legend()
    plt.savefig('grafico_rsi.png')
    plt.close()
    
    plt.figure(figsize=(12, 4))
    plt.plot(dados.index, dados['macd'], label='MACD', color='blue')
    plt.plot(dados.index, dados['sinal_macd'], label='Sinal MACD', color='red')
    plt.title('MACD e Sinal')
    plt.legend()
    plt.savefig('grafico_macd.png')
    plt.close()

def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Relatório de Análise Técnica - Solana (SOL)", ln=True, align="C")
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Este relatório apresenta uma análise técnica do ativo SOL (Solana) utilizando médias móveis, Bandas de Bollinger, RSI e MACD. Esses indicadores ajudam a identificar tendências, volatilidade e momentos de sobrecompra ou sobrevenda.")
    
    pdf.image("grafico_estrategia.png", x=10, y=50, w=180)
    pdf.ln(100)
    pdf.multi_cell(0, 10, "O gráfico acima mostra o preço de fechamento da Solana, junto com médias móveis e Bandas de Bollinger para medir a volatilidade.")
    
    pdf.add_page()
    pdf.image("grafico_rsi.png", x=10, y=30, w=180)
    pdf.ln(100)
    pdf.multi_cell(0, 10, "O RSI indica momentos em que o ativo pode estar sobrecomprado (acima de 70) ou sobrevendido (abaixo de 30), auxiliando na tomada de decisão para entradas e saídas de operações.")
    
    pdf.add_page()
    pdf.image("grafico_macd.png", x=10, y=30, w=180)
    pdf.ln(100)
    pdf.multi_cell(0, 10, "O MACD é um indicador de momentum usado para identificar mudanças na força da tendência. Quando o MACD cruza acima da linha de sinal, é um possível sinal de compra, e quando cruza abaixo, um possível sinal de venda.")
    
    pdf.add_page()
    pdf.multi_cell(0, 10, f"Retorno Acumulado: {dados['retorno_acumulado'].iloc[-1]:.2f}")
    pdf.multi_cell(0, 10, f"Volatilidade Média: {dados['retorno'].std():.4f}")
    pdf.output("analise_estrategia.pdf")

# Coleta de dados
dados = pegar_dados_yahoo("SOL-USD", "7d")

# Cálculo dos indicadores
dados = calcular_indicadores(dados)

# Geração de gráficos
gerar_graficos(dados)

# Geração do PDF
gerar_pdf(dados)

print("Relatório gerado com sucesso!")
