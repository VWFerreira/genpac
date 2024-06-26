import streamlit as st
from datetime import datetime
from pytz import timezone

# Configurar o layout
st.set_page_config(layout="wide", page_title="Relatório Banrisul")

# Carregar o arquivo CSS
with open("./css/app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Funções das páginas
from saldos import main as mostrar_saldos
from Valor_contrato import principal as mostrar_valor
from relatoriodiario import relatoriodiario as mostrar_relatorio
from gerar_contrato import gerar_contrato as gerar_contrato

PAGES = {
    "Contrato Geral": gerar_contrato,
    "Orçamentos": mostrar_valor,
    "Relatório Diário": mostrar_relatorio,
    "Saldos Contratos": mostrar_saldos,
}

# Título do Relatório
st.markdown("<h1 style='text-align: center; font-size: 48px;'>Relatório Banrisul</h1>", unsafe_allow_html=True)

# Data e Hora de Brasília
now = datetime.now(timezone('America/Sao_Paulo'))
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%Y-%m-%d")
current_day = now.strftime("%A")

st.markdown(
    f'''
    <div class="datetime">
        <p>Data: {current_date}</p>
        <p>Hora: {current_time}</p>
        <p>Dia da semana: {current_day}</p>
    </div>
    ''', 
    unsafe_allow_html=True,
)

st.sidebar.image("./image/logo.png", use_column_width=True)
st.sidebar.markdown("# Banrisul")

# Adicionar botões de navegação na barra lateral
selected_page = st.sidebar.radio("Selecione a página", list(PAGES.keys()))

if selected_page:
    page = PAGES[selected_page]
    page()
else:
    st.markdown('<div class="stAlert">Selecione uma página no menu acima.</div>', unsafe_allow_html=True)

