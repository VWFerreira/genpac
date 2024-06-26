import streamlit as st
import pandas as pd
from datetime import datetime

def carregar_dados(url):
    try:
        tabela = pd.read_csv(url)
        date_columns = ["DATA RECEBIDO", "DATA FINALIZADO", "DATA ORÇADO"]
        for col in date_columns:
            if col in tabela.columns:
                tabela[col] = pd.to_datetime(
                    tabela[col], format="%d/%m/%Y",
                    dayfirst=True, errors="coerce"
                ).dt.date
                
        tabela["VALOR ORÇADO"] = pd.to_numeric(
            tabela["VALOR ORÇADO"].str.replace(r"R\$", "").str.replace(".", "").str.replace(",", "."),
            errors="coerce",
        ).fillna(0)
        tabela["VALOR INSUMO"] = pd.to_numeric(
            tabela["VALOR INSUMO"].str.replace(r"R\$", "").str.replace(".", "").str.replace(",", "."),
            errors="coerce",
        ).fillna(0)
        tabela["VALOR MÃO DE OBRA"] = pd.to_numeric(
            tabela["VALOR MÃO DE OBRA"].str.replace(r"R\$", "").str.replace(".", "").str.replace(",", "."),
            errors="coerce",
        ).fillna(0)
        return tabela
    
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo CSV: {e}")
        return None

def calcular_metricas(tabela, contrato):
    hoje = datetime.now().date()
    filtro_contrato = tabela[tabela["CONTRATO"] == contrato]

    total_os_hoje = filtro_contrato[filtro_contrato["DATA RECEBIDO"] == hoje].shape[0]

    total_os_junho = filtro_contrato[
        (pd.to_datetime(filtro_contrato["DATA RECEBIDO"]).dt.month == 6)
        & (pd.to_datetime(filtro_contrato["DATA RECEBIDO"]).dt.year == 2024)
    ].shape[0]

    total_orcamentos_hoje = filtro_contrato[
        filtro_contrato["DATA ORÇADO"] == hoje
    ].shape[0]

    total_executadas_hoje = filtro_contrato[
        filtro_contrato["DATA FINALIZADO"] == hoje
    ].shape[0]

    return {
        "total_os_hoje": total_os_hoje,
        "total_os_junho": total_os_junho,
        "total_orcamentos_hoje": total_orcamentos_hoje,
        "total_executadas_hoje": total_executadas_hoje,
    }

def exibir_metricas_lote(tabela, contrato, titulo):
    metricas = calcular_metricas(tabela, contrato)

    st.subheader(titulo)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h4 style='font-size: 1.2rem;'>Total de OS Recebidas Lt1</h4>
                <p style='font-size: 1.5rem;'>{metricas['total_os_hoje']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h4>Total de OS Junho</h4>
                <p>{metricas['total_os_junho']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h4>Total de Orçamentos Hoje</h4>
                <p>{metricas['total_orcamentos_hoje']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h4>Total de OS Finalizadas Hoje</h4>
                <p>{metricas['total_executadas_hoje']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

def filtrar_ocorrencias(tabela, disciplinas, status_aberto, status_finalizado, contrato):
    abertas = tabela[
        tabela["DISCIPLINAS"].isin(disciplinas)
        & tabela["STATUS*"].isin(status_aberto)
        & (tabela["CONTRATO"] == contrato)
    ]
    finalizadas = tabela[
        tabela["DISCIPLINAS"].isin(disciplinas)
        & tabela["STATUS*"].isin(status_finalizado)
        & (tabela["CONTRATO"] == contrato)
    ]
    return len(abertas), len(finalizadas)

def calcular_percentual(abertas, finalizadas):
    total = abertas + finalizadas
    return (finalizadas / total) * 100 if total > 0 else 0

def exibir_resultados_lote(tabela, contrato, disciplinas, titulo):
    status_aberto = [
        "RECEBIDO",
        "ORÇADO",
        "COMPRAS",
        "EXECUÇÃO",
        "VERIFICAR",
        "PREVENTIVA",
        "LEVANTAMENTO",
        "EM ORÇAMENTO",
        "EM ESPERA",
        "PROGRAMADO",
    ]
    status_finalizado = ["FINALIZADO", "NOTA FISCAL", "EXECUTADO", "MEDIÇÃO"]

    abertas, finalizadas = filtrar_ocorrencias(
        tabela, disciplinas, status_aberto, status_finalizado, contrato
    )
    percentual = calcular_percentual(abertas, finalizadas)

    st.markdown(
        f"""
        <div class='lote-card'>
            <h4>{titulo}</h4>
            <p>Abertas: {abertas}</p>
            <p>Finalizadas: {finalizadas}</p>
            <p>Percentual: {percentual:.2f}%</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def exibir_tabelas(tabela):
    hoje = datetime.now().date()
    os_finalizadas_hoje = tabela[tabela["DATA FINALIZADO"] == hoje]
    total_disciplina_finalizadas_hoje = (
        os_finalizadas_hoje["DISCIPLINAS"].value_counts().reset_index()
    )
    total_disciplina_finalizadas_hoje.columns = ["Disciplina", "Quantidade"]

    st.markdown("<h2 class='custom-subheader'>Total de Disciplinas Finalizadas Hoje</h2>", unsafe_allow_html=True)
    for _, row in total_disciplina_finalizadas_hoje.iterrows():
        st.markdown(
            f"<div><span class='custom-disciplina'>{row['Disciplina']}:</span> <span class='custom-quantidade'>{row['Quantidade']}</span></div>",
            unsafe_allow_html=True,
        )

def relatoriodiario():
    with open("./css/reldiario.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    url = "https://docs.google.com/spreadsheets/d/1vp62n11C8Gnx9QMHL08QofGnNdlt08P54EJ7bkOHVaE/export?format=csv"
    tabela = carregar_dados(url)
    if tabela is not None:
        st.write('<p style="font-size:26px;">Resultados Lote 01 e Lote 02</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4, gap="large")
        
        with col1:
            exibir_resultados_lote(
                tabela,
                "0100215/2023",
                [
                    "ALVENARIA",
                    "HIDRÁULICA",
                    "CIVIL",
                    "COBERTURA",
                    "COMUNICAÇÃO VISUAL",
                    "DRYWALL",
                    "INSUMOS E EQUIPAMENTOS",
                    "IMPERMEABILIZAÇÃO",
                    "MARCENARIA",
                    "PINTURA",
                    "SERRALHERIA",
                    "VIDRAÇARIA",
                    "PERSIANA",
                    "EXTINTOR",
                ],
                "CIVIL LT1",
            )
        with col2:
            exibir_resultados_lote(
                tabela,
                "0100215/2023",
                ["ELÉTRICA"],
                "ELÉTRICA LT1",
            )
        with col3:
            exibir_resultados_lote(
                tabela,
                "0200215/2023",
                [
                    "ALVENARIA",
                    "HIDRÁULICA",
                    "CIVIL",
                    "COBERTURA",
                    "COMUNICAÇÃO VISUAL",
                    "DRYWALL",
                    "INSUMOS E EQUIPAMENTOS",
                    "IMPERMEABILIZAÇÃO",
                    "MARCENARIA",
                    "PINTURA",
                    "SERRALHERIA",
                    "VIDRAÇARIA",
                    "PERSIANA",
                    "EXTINTOR",
                ],
                "CIVIL LT2",
            )
        with col4:
            exibir_resultados_lote(
                tabela,
                "0200215/2023",
                ["ELÉTRICA"],
                "ELÉTRICA LT2",
            )

        st.markdown(
            """
            <div class='metric-subtitle'>
                <h4>Métricas Lote 01 e Lote 02</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col5, col6, col7, col8 = st.columns(4, gap="large")
        
        with col5:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Recebidas Hoje - Lote 01</h4>
                    <p>{calcular_metricas(tabela, "0100215/2023")['total_os_hoje']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col6:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Junho - Lote 01</h4>
                    <p>{calcular_metricas(tabela, "0100215/2023")['total_os_junho']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col7:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Recebidas Hoje - Lote 02</h4>
                    <p>{calcular_metricas(tabela, "0200215/2023")['total_os_hoje']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col8:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Junho - Lote 02</h4>
                    <p>{calcular_metricas(tabela, "0200215/2023")['total_os_junho']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        col9, col10, col11, col12 = st.columns(4, gap="large")
        
        with col9:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de Orçamentos Hoje - Lote 01</h4>
                    <p>{calcular_metricas(tabela, "0100215/2023")['total_orcamentos_hoje']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col10:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Finalizadas Hoje - Lote 01</h4>
                    <p>{calcular_metricas(tabela, "0100215/2023")['total_executadas_hoje']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col11:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de Orçamentos Hoje - Lote 02</h4>
                    <p>{calcular_metricas(tabela, "0200215/2023")['total_orcamentos_hoje']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col12:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Finalizadas Hoje - Lote 02</h4>
                    <p>{calcular_metricas(tabela, "0200215/2023")['total_executadas_hoje']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        total_os_recebidas_hoje = calcular_metricas(tabela, "0100215/2023")['total_os_hoje'] + calcular_metricas(tabela, "0200215/2023")['total_os_hoje']
        total_os_finalizadas = calcular_metricas(tabela, "0100215/2023")['total_executadas_hoje'] + calcular_metricas(tabela, "0200215/2023")['total_executadas_hoje']
        total_orcamentos = calcular_metricas(tabela, "0100215/2023")['total_orcamentos_hoje'] + calcular_metricas(tabela, "0200215/2023")['total_orcamentos_hoje']
        total_os_junho = calcular_metricas(tabela, "0100215/2023")['total_os_junho'] + calcular_metricas(tabela, "0200215/2023")['total_os_junho']
        
        st.markdown(
            """
            <div class='metric-subtitle'>
                <h4>Métricas Consolidadas Totais</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col13, col14, col15, col16 = st.columns(4, gap="large")

        with col13:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Recebidas</h4>
                    <p>{total_os_recebidas_hoje}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col14:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Finalizadas</h4>
                    <p>{total_os_finalizadas}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col15:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de Orçamentos</h4>
                    <p>{total_orcamentos}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col16:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <h4>Total de OS Junho</h4>
                    <p>{total_os_junho}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div class='horizontal-line'></div>", unsafe_allow_html=True)
        exibir_tabelas(tabela)

if __name__ == "__main__":
    relatoriodiario()
