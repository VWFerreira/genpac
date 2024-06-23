import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import base64

def convert_currency(value):
    if isinstance(value, str):
        return float(
            value.replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
    return value

@st.cache_data(ttl=60)
def load_data(csv_url):
    df = pd.read_csv(csv_url)
    df = df[
        ~df["VALOR"].astype(str).str.contains("nan|http")
    ].copy()
    df["VALOR"] = df["VALOR"].apply(convert_currency)
    df["SALDO L1"] = df["SALDO L1"].apply(convert_currency)
    df["SALDO L2"] = df["SALDO L2"].apply(convert_currency)

    df["MES_ANO"] = df["MES"].astype(str) + '/' + df["ANO"].astype(str)
    return df

def main():
    csv_url = (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSlTQoxa_YIMgRHv5x-"
        "URXirElC2efKea8CKK4U2qhqIKJPg_Zgv6IKZFVRCMNhYlohC0la69ueAyL_/"
        "pub?gid=713266789&single=true&output=csv"
    )

    with st.spinner("Carregando dados..."):
        df = load_data(csv_url)

    summary_stats = df[["VALOR", "SALDO L1", "SALDO L2"]].describe()

    monthly_totals = df.groupby("MES_ANO")["VALOR"].sum().reset_index()

    total_paid_lote1 = df[
        (df["LOTE"] == "LOTE 01") & (df["STATUS"] == "PAGO")
    ]["VALOR"].sum()
    total_paid_lote2 = df[
        (df["LOTE"] == "LOTE 02") & (df["STATUS"] == "PAGO")
    ]["VALOR"].sum()
    pending_payments_lote1 = df[
        (df["LOTE"] == "LOTE 01") & (df["STATUS"] != "PAGO")
    ]["VALOR"].sum()
    pending_payments_lote2 = df[
        (df["LOTE"] == "LOTE 02") & (df["STATUS"] != "PAGO")
    ]["VALOR"].sum()

    total_saldo_lote1 = df["SALDO L1"].sum()
    total_saldo_lote2 = df["SALDO L2"].sum()

    saldo_difference = total_saldo_lote1 - total_saldo_lote2

    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    total_mes = pending_payments_lote1 + pending_payments_lote2

    with open("./css/saldos.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([5, 2])

    with col1:
        st.markdown(
            '<h3 class="contract">CONTRATO 0100215/2023: R$ 4.500,000 ||| CONTRATO 0200215/2023: R$ 2.900,000</h3>',
            unsafe_allow_html=True
        )

    col1, col2 = st.columns([1, 5])
    with col1:
        nota_fiscal = st.text_input("Número da Nota Fiscal")
        mes = st.selectbox(
            "Mês", options=["Todos"] + list(df["MES_ANO"].unique())
        )

    filtered_df = df.copy()
    if nota_fiscal:
        filtered_df = filtered_df[
            filtered_df["NOTA FISCAL"]
            .astype(str)
            .str.contains(nota_fiscal)
        ]
    if mes != "Todos":
        filtered_df = filtered_df[
            filtered_df["MES_ANO"] == mes
        ]

    monthly_totals_filtered = filtered_df.groupby(
        "MES_ANO"
    )["VALOR"].sum().reset_index()

    chart = (
        alt.Chart(monthly_totals_filtered)
        .mark_bar()
        .encode(
            x=alt.X('MES_ANO', title='Mês e Ano', sort=None),
            y='VALOR',
            tooltip=["MES_ANO", "VALOR"],
            color=alt.value("#8B0000"),
        )
        .properties(
            title="Total de Faturas por Mês",
            width=600,
            height=400,
        )
    )

    with col2:
        st.altair_chart(chart, use_container_width=True)

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Total Pago Lote 1: </span><span class="stMetric-value">R$ '
            f'{total_paid_lote1:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Saldo Lote 1: </span><span class="stMetric-value">R$ '
            f'{summary_stats.loc["mean", "SALDO L1"]:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Total Pago Lote 2:</span><span class="stMetric-value">R$ '
            f'{total_paid_lote2:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Saldo Lote 2: </span><span class="stMetric-value">R$ '
            f'{summary_stats.loc["mean", "SALDO L2"]:,.2f}</span></div>',
            unsafe_allow_html=True,
        )

    col7, col8, col9, col10 = st.columns(4)
    with col7:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Aguardando Pagamento Lote 1: </span><span class="stMetric-value">R$ '
            f'{pending_payments_lote1:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col8:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Aguardando Pagamento Lote 2: </span><span class="stMetric-value">R$ '
            f'{pending_payments_lote2:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col9:
        avg_invoice_value = df["VALOR"].mean()
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Vl.Médio NFs: </span><span class="stMetric-value">R$ '
            f'{avg_invoice_value:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col10:
        total_invoices = df["NOTA FISCAL"].count()
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'NF: Quantidade: </span><span class="stMetric-value">'
            f'{total_invoices}</span></div>',
            unsafe_allow_html=True,
        )

    col11, col12, col13, col14 = st.columns(4)
    with col11:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Saldo Total Lote 1: </span><span class="stMetric-value">R$ '
            f'{total_saldo_lote1:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col12:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Saldo Total Lote 2: </span><span class="stMetric-value">R$ '
            f'{total_saldo_lote2:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col13:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Diferença entre Saldos L1 e L2 : </span><span class="stMetric-value">R$'
            f'{saldo_difference:,.2f}</span></div>',
            unsafe_allow_html=True,
        )
    with col14:
        st.markdown(
            f'<div class="stMetric-container"><span class="stMetric-label">'
            f'Total Mes Junho : </span><span class="stMetric-value">R$'
            f'{total_mes:,.2f}</span></div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
