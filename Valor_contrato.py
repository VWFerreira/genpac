import streamlit as st
import pandas as pd
from datetime import datetime
import base64

@st.cache_data(ttl=60)
def load_data(url):
    data = pd.read_csv(url)
    data = clean_data(data)
    return data

def clean_data(data):
    columns_to_clean = ["VALOR ORÇADO", "VALOR INSUMO", "VALOR MÃO DE OBRA"]
    for column in columns_to_clean:
        data[column] = pd.to_numeric(
            data[column]
            .str.replace("R$", "")
            .str.replace(".", "")
            .str.replace(",", ".")
            .str.strip(),
            errors="coerce",
        )
    data["DATA ORÇADO"] = pd.to_datetime(
        data["DATA ORÇADO"], format="%d/%m/%Y", errors="coerce"
    )
    return data

def filter_data(data, contract, date_filter, value_column):
    filtered_data = data[
        (data["STATUS*"].str.lower() == "finalizado") & (data["CONTRATO"] == contract)
    ]
    if date_filter == "today":
        today = datetime.now().date()
        filtered_data = filtered_data[filtered_data["DATA ORÇADO"].dt.date == today]
    elif date_filter == "june_2024":
        june_2024_start = datetime(2024, 6, 1)
        june_2024_end = datetime(2024, 6, 30)
        filtered_data = filtered_data[
            (filtered_data["DATA ORÇADO"] >= june_2024_start) &
            (filtered_data["DATA ORÇADO"] <= june_2024_end)
        ]
    return filtered_data[value_column].sum()

def calculate_previa_medicao_june(data, contract):
    june_2024_start = datetime(2024, 6, 1)
    june_2024_end = datetime(2024, 6, 30)
    filtered_data = data[
        (data["STATUS*"].str.lower() == "finalizado") &
        (data["CONTRATO"] == contract) &
        (data["DATA ORÇADO"] >= june_2024_start) &
        (data["DATA ORÇADO"] <= june_2024_end)
    ]
    return filtered_data["VALOR ORÇADO"].sum()

def calculate_totals(data, contract):
    # Condição que verifica se o status é "FINALIZADO" e se o contrato corresponde ao contrato fornecido
    condition = (data["STATUS*"].str.lower() == "finalizado") & (data["CONTRATO"] == contract)
    
    # Filtrando os dados com a condição
    filtered_data = data[condition]
    
    # Calculando os totais
    total_insumo = filtered_data["VALOR INSUMO"].sum()
    total_mao_de_obra = filtered_data["VALOR MÃO DE OBRA"].sum()
    total_orcado = filtered_data["VALOR ORÇADO"].sum()
    
    return total_insumo, total_mao_de_obra, total_orcado

def create_metric_box(label, value):
    return f"""
    <div class="metric-box">
        <h4>{label}</h4>
        <p>{value}</p>
    </div>
    """

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def display_metrics(data):
    today_metrics = {
        "0100215/2023": {
            "budget": filter_data(data, "0100215/2023", "today", "VALOR ORÇADO"),
            "insumo": filter_data(data, "0100215/2023", "today", "VALOR INSUMO"),
            "mao_de_obra": filter_data(data, "0100215/2023", "today", "VALOR MÃO DE OBRA")
        },
        "0200215/2023": {
            "budget": filter_data(data, "0200215/2023", "today", "VALOR ORÇADO"),
            "insumo": filter_data(data, "0200215/2023", "today", "VALOR INSUMO"),
            "mao_de_obra": filter_data(data, "0200215/2023", "today", "VALOR MÃO DE OBRA")
        }
    }

    june_2024_metrics = {
        "0100215/2023": {
            "budget": filter_data(data, "0100215/2023", "june_2024", "VALOR ORÇADO"),
            "insumo": filter_data(data, "0100215/2023", "june_2024", "VALOR INSUMO"),
            "mao_de_obra": filter_data(data, "0100215/2023", "june_2024", "VALOR MÃO DE OBRA")
        },
        "0200215/2023": {
            "budget": filter_data(data, "0200215/2023", "june_2024", "VALOR ORÇADO"),
            "insumo": filter_data(data, "0200215/2023", "june_2024", "VALOR INSUMO"),
            "mao_de_obra": filter_data(data, "0200215/2023", "june_2024", "VALOR MÃO DE OBRA")
        }
    }

    previa_medicao_june = {
        "0100215/2023": calculate_previa_medicao_june(data, "0100215/2023"),
        "0200215/2023": calculate_previa_medicao_june(data, "0200215/2023")
    }

    total_metrics = {
        "0100215/2023": calculate_totals(data, "0100215/2023"),
        "0200215/2023": calculate_totals(data, "0200215/2023")
    }

    total_insumo = total_metrics["0100215/2023"][0] + total_metrics["0200215/2023"][0]
    total_mao_de_obra = total_metrics["0100215/2023"][1] + total_metrics["0200215/2023"][1]
    total_orcado = total_metrics["0100215/2023"][2] + total_metrics["0200215/2023"][2]
    total_medicao = previa_medicao_june["0100215/2023"] + previa_medicao_june["0200215/2023"]

    st.markdown('<p class="subheader-lote">Lote 1 0100215/2023</p>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(create_metric_box("Valor Orçado - Hoje",
                    f"R$ {today_metrics['0100215/2023']['budget']:,.2f}"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_box("Valor Insumo - Hoje",
                    f"R$ {today_metrics['0100215/2023']['insumo']:,.2f}"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_box("Valor Mão de Obra - Hoje", f"R$ {today_metrics['0100215/2023']['mao_de_obra']:,.2f}"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_box("Valor Orçado - Junho 2024", f"R$ {june_2024_metrics['0100215/2023']['budget']:,.2f}"), unsafe_allow_html=True)
    with col5:
        st.markdown(create_metric_box("Valor Insumo - Junho 2024", f"R$ {june_2024_metrics['0100215/2023']['insumo']:,.2f}"), unsafe_allow_html=True)
    with col6:
        st.markdown(create_metric_box("Valor Mão de Obra - Junho 2024", f"R$ {june_2024_metrics['0100215/2023']['mao_de_obra']:,.2f}"), unsafe_allow_html=True)

    st.markdown('<p class="subheader-lote">Lote 2 0200215/2023</p>', unsafe_allow_html=True)
    col8, col9, col10, col11, col12, col13 = st.columns(6)
    with col8:
        st.markdown(create_metric_box("Valor Orçado - Hoje",
                    f"R$ {today_metrics['0200215/2023']['budget']:,.2f}"), unsafe_allow_html=True)
    with col9:
        st.markdown(create_metric_box("Valor Insumo - Hoje",
                    f"R$ {today_metrics['0200215/2023']['insumo']:,.2f}"), unsafe_allow_html=True)
    with col10:
        st.markdown(create_metric_box("Valor Mão de Obra - Hoje", f"R$ {today_metrics['0200215/2023']['mao_de_obra']:,.2f}"), unsafe_allow_html=True)
    with col11:
        st.markdown(create_metric_box("Valor Orçado - Junho 2024", f"R$ {june_2024_metrics['0200215/2023']['budget']:,.2f}"), unsafe_allow_html=True)
    with col12:
        st.markdown(create_metric_box("Valor Insumo - Junho 2024", f"R$ {june_2024_metrics['0200215/2023']['insumo']:,.2f}"), unsafe_allow_html=True)
    with col13:
        st.markdown(create_metric_box("Valor Mão de Obra - Junho 2024", f"R$ {june_2024_metrics['0200215/2023']['mao_de_obra']:,.2f}"), unsafe_allow_html=True)

    st.markdown('<p class="subheader-lote">Totais</p>', unsafe_allow_html=True)
    col14, col15, col16, col17 = st.columns(4)
    with col14:
        st.markdown(create_metric_box("Total Valor Insumo", f"R$ {total_insumo:,.2f}"), unsafe_allow_html=True)
    with col15:
        st.markdown(create_metric_box("Total Valor Mão de Obra", f"R$ {total_mao_de_obra:,.2f}"), unsafe_allow_html=True)
    with col16:
        st.markdown(create_metric_box("Total Valor Orçado - Junho 2024",
                    f"R$ {total_orcado:,.2f}"), unsafe_allow_html=True)
    with col17:
        st.markdown(create_metric_box("Total Medição - Junho 2024",
                    f"R$ {total_medicao:,.2f}"), unsafe_allow_html=True)

    st.markdown('<p class="subheader-lote">Previa de Medição - Junho 2024</p>', unsafe_allow_html=True)
    col18, col19 = st.columns(2)
    with col18:
        st.markdown(create_metric_box("Lote 1 - Contrato 0100215/2023",
                    f"R$ {previa_medicao_june['0100215/2023']:,.2f}"), unsafe_allow_html=True)
    with col19:
        st.markdown(create_metric_box("Lote 2 - Contrato 0200215/2023",
                    f"R$ {previa_medicao_june['0200215/2023']:,.2f}"), unsafe_allow_html=True)

def principal():
    url = "https://docs.google.com/spreadsheets/d/1vp62n11C8Gnx9QMHL08QofGnNdlt08P54EJ7bkOHVaE/export?format=csv"
    data = load_data(url)

    with open("./css/valor.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    display_metrics(data)


if __name__ == "__main__":
    principal()
