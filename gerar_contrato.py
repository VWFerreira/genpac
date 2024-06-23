import pandas as pd
import streamlit as st
import calendar
import altair as alt

def gerar_contrato():
    st.write("---")

    url = (
        "https://docs.google.com/"
        "spreadsheets/d/"
        "1vp62n11C8Gnx9QMHL08QofGnNdlt08P54EJ7bkOHVaE/"
        "export?format=csv"
    )

    try:
        tabela = pd.read_csv(url, parse_dates=["DATA RECEBIDO"], dayfirst=True)

        contratos_interesse = ["0100215/2023", "0200215/2023"]
        filtro_contratos = tabela["CONTRATO"].isin(contratos_interesse)
        dados_filtrados = tabela[filtro_contratos]

        contagem_os = dados_filtrados["CONTRATO"].value_counts()

        total_os = contagem_os.sum()

        st.subheader("Total de Ordens de Serviços recebidas por Contrato")

        tabela["DATA RECEBIDO"] = pd.to_datetime(
            tabela["DATA RECEBIDO"], format="%d/%m/%Y", dayfirst=True, errors="coerce"
        )

        tabela["DATA FINALIZADO"] = pd.to_datetime(
            tabela["DATA FINALIZADO"], format="%d/%m/%Y", dayfirst=True, errors="coerce"
        )

        junho_2024 = tabela[
            (tabela["DATA RECEBIDO"].dt.month == 6) & (tabela["DATA RECEBIDO"].dt.year == 2024)
        ]
        total_os_junho = junho_2024.shape[0]

        col1, col2, col3, col4, col5 = st.columns(5, gap="small")

        with col1:
            data_pie = pd.DataFrame(
                {
                    "Contrato": contratos_interesse,
                    "Quantidade": [
                        contagem_os.get(contratos_interesse[0], 0),
                        contagem_os.get(contratos_interesse[1], 0),
                    ],
                }
            )

            pie_chart = (
                alt.Chart(data_pie)
                .mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta(field="Quantidade", type="quantitative"),
                    color=alt.Color(field="Contrato", type="nominal"),
                    tooltip=["Contrato", "Quantidade"],
                )
                .properties(width=150, height=150)
            )

            st.altair_chart(pie_chart, use_container_width=True)

        with col2:
            contrato_1 = contratos_interesse[0]
            count_1 = contagem_os.get(contrato_1, 0)
            st.markdown(
                f"<div style='font-size:18px; text-align:center; color:#FFFAFA;font-weight:bold;'>Lote1 {contrato_1}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:36px; text-align:center; color:#1E90FF;font-weight:bold;'>{count_1}</div>",
                unsafe_allow_html=True,
            )

        with col3:
            contrato_2 = contratos_interesse[1]
            count_2 = contagem_os.get(contrato_2, 0)
            st.markdown(
                f"<div style='font-size:18px; text-align:center; color:#FFFAFA; font-weight:bold;'>Lote2 {contrato_2}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:36px; text-align:center; color:#1E90FF; font-weight:bold;'>{count_2}</div>",
                unsafe_allow_html=True,
            )

        with col5:
            st.markdown(
                f"<div style='font-size:28px; text-align:center; color:#FFFAFA; font-weight:bold;'>Total Geral</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:36px; text-align:center; color:#1E90FF; font-weight:bold;'>{total_os}</div>",
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"<div style='font-size:18px; text-align:center; color:#FFFAFA;font-weight:bold;'>Recebidas Junho 2024</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:36px; text-align:center; color:#FFD700;font-weight:bold;'>{total_os_junho}</div>",
                unsafe_allow_html=True,
            )

        st.write("---")

        dados_filtrados = tabela[(tabela["DATA RECEBIDO"].dt.year.isin([2023, 2024]))]

        col4, col5 = st.columns([5, 1])

        with col5:
            st.write("Selecionar Período")
            inicio_mes = st.selectbox(
                "Mês Inicial", range(1, 13), 0, key="inicio_mes1")
            inicio_ano = st.selectbox(
                "Ano Inicial", [2023, 2024], 0, key="inicio_ano1")
            fim_mes = st.selectbox(
                "Mês Final", range(1, 13), 11, key="fim_mes1")
            fim_ano = st.selectbox(
                "Ano Final", [2023, 2024], 1, key="fim_ano1")

        inicio_data = pd.Timestamp(year=inicio_ano, month=inicio_mes, day=1)
        fim_data = pd.Timestamp(
            year=fim_ano, month=fim_mes, day=calendar.monthrange(fim_ano, fim_mes)[1]
        )
        dados_selecionados = dados_filtrados[
            (dados_filtrados["DATA RECEBIDO"] >= inicio_data) & (dados_filtrados["DATA RECEBIDO"] <= fim_data)
        ]

        os_por_mes = (
            dados_selecionados.groupby(
                dados_selecionados["DATA RECEBIDO"].dt.to_period("M")
            )
            .size()
            .reset_index(name="Quantidade de OS")
        )

        os_por_mes["MES"] = os_por_mes["DATA RECEBIDO"].dt.strftime("%b %Y")

        chart = (
            alt.Chart(os_por_mes)
            .mark_bar()
            .encode(
                x="MES",
                y="Quantidade de OS",
                color=alt.value("#FF0000"),
            )
            .properties(
                title=f"Quantidade de (OS) recebidas por Mês ({inicio_mes}/{inicio_ano} a {fim_mes}/{fim_ano})"
            )
        )
        col4.altair_chart(chart, use_container_width=True)

        st.write("---")

        col1, col2 = st.columns([1, 6])

        with col1:
            st.write("Selecionar Período")
            inicio_data = st.date_input(
                "Data Inicial", value=pd.to_datetime("2023-07-01"), key="inicio_data2"
            )
            fim_data = st.date_input(
                "Data Final", value=pd.to_datetime("2025-12-31"), key="fim_data2"
            )

        dados_selecionados = dados_filtrados[
            (dados_filtrados["DATA RECEBIDO"] >= pd.to_datetime(inicio_data)) &
            (dados_filtrados["DATA RECEBIDO"] <= pd.to_datetime(fim_data))
        ]

        os_por_dia = (
            dados_selecionados.groupby(
                pd.to_datetime(dados_selecionados["DATA RECEBIDO"]).dt.date
            )
            .size()
            .reset_index(name="QUANTIDADE")
        )

        with col2:
            st.subheader("Total de OS recebidas por dia")
            chart = (
                alt.Chart(os_por_dia)
                .mark_bar(color="#1E90FF")
                .encode(x="DATA RECEBIDO:T", y="QUANTIDADE:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart, use_container_width=True)

        st.write("---")

        col1, col2, col3 = st.columns([1, 6, 1])

        with col3:
            st.write("Selecionar Período")
            inicio_data = st.date_input(
                "Data Inicial", value=pd.to_datetime("2023-07-01"), key="inicio_data4"
            )
            fim_data = st.date_input(
                "Data Final", value=pd.to_datetime("2025-12-31"), key="fim_data4"
            )

        disciplinas = tabela["DISCIPLINAS"].unique().tolist()
        disciplinas.insert(0, "Todas as disciplinas")

        with col1:
            disciplina_selecionada = st.selectbox(
                "Selecione a disciplina", disciplinas, key="disciplina_selecionada1"
            )

        dados_filtrados = tabela[
            (tabela["DATA RECEBIDO"] >= pd.to_datetime(inicio_data)) &
            (tabela["DATA RECEBIDO"] <= pd.to_datetime(fim_data))
        ]

        if disciplina_selecionada != "Todas as disciplinas":
            dados_filtrados = dados_filtrados[
                dados_filtrados["DISCIPLINAS"] == disciplina_selecionada
            ]

        os_por_dia = (
            dados_filtrados.groupby(
                pd.to_datetime(dados_filtrados["DATA RECEBIDO"]).dt.date
            )
            .size()
            .reset_index(name="QUANTIDADE")
        )

        total_os = dados_filtrados.shape[0]

        with col2:
            st.markdown(
                f"<h4>Quantidade de OS recebidas por dia de <span style='color:#1E90FF;'>{inicio_data}</span> a <span style='color:#1E90FF;'>{fim_data}</span> - <span style='color:#1E90FF;'>{disciplina_selecionada}</span> (Total: <span style='color:#1E90FF;'>{total_os}</span>)</h4>",
                unsafe_allow_html=True,
            )
            chart = (
                alt.Chart(os_por_dia)
                .mark_bar(color="#FF0000")
                .encode(x="DATA RECEBIDO:T", y="QUANTIDADE:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart, use_container_width=True)

        st.write("---")

        col1, col2, col3 = st.columns([1, 6, 1])

        with col1:
            st.write("Selecionar Período")
            inicio_data = st.date_input(
                "Data Inicial", value=pd.to_datetime("2023-07-01"), key="inicio_data5"
            )
            fim_data = st.date_input(
                "Data Final", value=pd.to_datetime("2025-12-31"), key="fim_data5"
            )

        with col3:
            status_opcoes = tabela["STATUS*"].unique().tolist()
            status_opcoes.insert(0, "Todos os status")
            status_selecionado = st.selectbox(
                "Selecione o status", status_opcoes, key="status_selecionado1"
            )

        dados_filtrados = tabela[
            (tabela["DATA RECEBIDO"] >= pd.to_datetime(inicio_data)) &
            (tabela["DATA RECEBIDO"] <= pd.to_datetime(fim_data))
        ]

        if status_selecionado == "Todos os status":
            dados_filtrados_status = dados_filtrados
        else:
            dados_filtrados_status = dados_filtrados[
                dados_filtrados["STATUS*"] == status_selecionado
            ]

        os_por_dia_status = (
            dados_filtrados_status.groupby(
                pd.to_datetime(dados_filtrados_status["DATA RECEBIDO"]).dt.date
            )
            .size()
            .reset_index(name="QUANTIDADE")
        )

        total_os_status = dados_filtrados_status.shape[0]

        with col2:
            st.markdown(
                f"<h4>Quantidade de OS recebidas por dia de <span style='color:#1E90FF;'>{inicio_data}</span> a <span style='color:#1E90FF;'>{fim_data}</span> - <span style='color:#1E90FF;'>{status_selecionado}</span> (Total: <span style='color:#1E90FF;'>{total_os_status}</span>)</h4>",
                unsafe_allow_html=True,
            )
            chart = (
                alt.Chart(os_por_dia_status)
                .mark_bar(color="#1E90FF")
                .encode(x="DATA RECEBIDO:T", y="QUANTIDADE:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart, use_container_width=True)

        st.write("---")

        def calcular_percentual(abertas, finalizadas):
            total = abertas + finalizadas
            return (finalizadas / total) * 100 if total > 0 else 0

        def exibir_container1(titulo, abertas, finalizadas, percentual, cor):
            with st.container():
                st.subheader(titulo)
                st.write(f"Abertas: {abertas}")
                st.write(f"Finalizadas: {finalizadas}")
                st.write(f"Percentual: {percentual:.2f}%")
                st.progress(percentual / 100.0)

        def filtrar_ocorrencias(
            disciplinas, status_aberto, status_finalizado, contrato
        ):
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

        status_finalizado = ["FINALIZADO",
                             "NOTA FISCAL", "EXECUTADO", "MEDIÇÃO"]

        disciplinas_civil = [
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
        ]

        abertas_0100215_civil, finalizadas_0100215_civil = filtrar_ocorrencias(
            disciplinas_civil, status_aberto, status_finalizado, "0100215/2023"
        )
        percentual_0100215_civil = calcular_percentual(
            abertas_0100215_civil, finalizadas_0100215_civil
        )

        abertas_0100215_eletrica, finalizadas_0100215_eletrica = filtrar_ocorrencias(
            ["ELÉTRICA"], status_aberto, status_finalizado, "0100215/2023"
        )
        percentual_0100215_eletrica = calcular_percentual(
            abertas_0100215_eletrica, finalizadas_0100215_eletrica
        )

        abertas_0200215_civil, finalizadas_0200215_civil = filtrar_ocorrencias(
            disciplinas_civil, status_aberto, status_finalizado, "0200215/2023"
        )
        percentual_0200215_civil = calcular_percentual(
            abertas_0200215_civil, finalizadas_0200215_civil
        )

        abertas_0200215_eletrica, finalizadas_0200215_eletrica = filtrar_ocorrencias(
            ["ELÉTRICA"], status_aberto, status_finalizado, "0200215/2023"
        )
        percentual_0200215_eletrica = calcular_percentual(
            abertas_0200215_eletrica, finalizadas_0200215_eletrica
        )

        st.markdown('<link rel="stylesheet" href="styles.css">',
                    unsafe_allow_html=True)

        def exibir_container1(titulo, abertas, finalizadas, percentual, cor):
            st.markdown(
                f'<p class="small-font"><strong>{titulo}</strong></p>',
                unsafe_allow_html=True,
            )
            st.write(f"Abertas: {abertas}")
            st.write(f"Finalizadas: {finalizadas}")
            st.write(f"Percentual: {percentual:.2f}%")
            st.progress(percentual / 100.0)

        st.markdown(
            '<p class="small-font"><strong>Resultados:</strong></p>',
            unsafe_allow_html=True,
        )
        container = st.container()
        with container:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                exibir_container1(
                    "Lote 01 Contrato 0100215/2023 - CIVIL",
                    abertas_0100215_civil,
                    finalizadas_0100215_civil,
                    percentual_0100215_civil,
                    "blue",
                )

            with col2:
                exibir_container1(
                    "Lote 01 Contrato 0100215/2023 - ELÉTRICA",
                    abertas_0100215_eletrica,
                    finalizadas_0100215_eletrica,
                    percentual_0100215_eletrica,
                    "green",
                )

            with col3:
                exibir_container1(
                    "Lote 02 Contrato 0200215/2023 - CIVIL",
                    abertas_0200215_civil,
                    finalizadas_0200215_civil,
                    percentual_0200215_civil,
                    "orange",
                )

            with col4:
                exibir_container1(
                    "Lote 02 Contrato 0200215/2023 - ELÉTRICA",
                    abertas_0200215_eletrica,
                    finalizadas_0200215_eletrica,
                    percentual_0200215_eletrica,
                    "red",
                )
            st.write("---")

            junho_2024_finalizado = tabela[
                (tabela["DATA FINALIZADO"].dt.month == 6) & (tabela["DATA FINALIZADO"].dt.year == 2024)
            ]

            junho_2024_finalizado["DATA FINALIZADO"] = pd.to_datetime(
                junho_2024_finalizado["DATA FINALIZADO"].copy()
            ).dt.strftime("%d/%m/%Y")

            finalizado_0100215 = junho_2024_finalizado[
                junho_2024_finalizado["CONTRATO"] == "0100215/2023"
            ]
            finalizado_0200215 = junho_2024_finalizado[
                junho_2024_finalizado["CONTRATO"] == "0200215/2023"
            ]

            os_finalizado_por_dia_0100215 = (
                finalizado_0100215.groupby("DATA FINALIZADO")
                .size()
                .reset_index(name="QUANTIDADE")
            )

            os_finalizado_por_dia_0200215 = (
                finalizado_0200215.groupby("DATA FINALIZADO")
                .size()
                .reset_index(name="QUANTIDADE")
            )

            os_finalizado_por_dia = (
                junho_2024_finalizado.groupby("DATA FINALIZADO")
                .size()
                .reset_index(name="QUANTIDADE")
            )

            col1, col2, col3 = st.columns([4, 1, 1])

            with col3:
                st.markdown(
                    '<p style="font-size: 13px; color:  #FF0000;text-align: center;"><strong>OS Finalizadas Contrato 0100215/2023</strong></p>',
                    unsafe_allow_html=True,
                )
                st.write(os_finalizado_por_dia_0100215)

            with col2:
                st.markdown(
                    '<p style="font-size: 13px; color: #FF0000;text-align: center;"><strong>OS Finalizadas Contrato 0200215/2023</strong></p>',
                    unsafe_allow_html=True,
                )
                st.write(os_finalizado_por_dia_0200215)

            with col1:
                st.markdown(
                    '<p class="font" style="font-size:26px;"><strong>OS Finalizadas por Dia em Junho de 2024</strong></p>',
                    unsafe_allow_html=True,
                )
                chart = (
                    alt.Chart(os_finalizado_por_dia)
                    .mark_bar(color="#FF0000")
                    .encode(x="DATA FINALIZADO:T", y="QUANTIDADE:Q")
                    .properties(width=600, height=400)
                )
                st.altair_chart(chart, use_container_width=True)

            st.write("---")

            def calcular_media_execucao_por_dia(df, ano):
                df = df.copy()
                df["DATA FINALIZADO"] = pd.to_datetime(df["DATA FINALIZADO"])
                df_ano = df[df["DATA FINALIZADO"].dt.year == ano].copy()
                df_ano.loc[:, "DATA FINALIZADO"] = df_ano[
                    "DATA FINALIZADO"
                ].dt.strftime("%d/%m/%Y")

                os_finalizado_por_dia = (
                    df_ano.groupby("DATA FINALIZADO")
                    .size()
                    .reset_index(name="QUANTIDADE")
                )

                media_execucao_por_dia = (
                    os_finalizado_por_dia.groupby(
                        "DATA FINALIZADO")["QUANTIDADE"]
                    .mean()
                    .reset_index(name="MEDIA_EXECUCAO")
                )

                media_geral_ano = media_execucao_por_dia["MEDIA_EXECUCAO"].mean(
                )

                return media_execucao_por_dia, media_geral_ano

            junho_2024_finalizado = tabela[
                (tabela["DATA FINALIZADO"].dt.month == 6) & (tabela["DATA FINALIZADO"].dt.year == 2024)
            ]

            media_execucao_junho_2024, media_geral_junho_2024 = (
                calcular_media_execucao_por_dia(junho_2024_finalizado, 2024)
            )

            media_execucao_2023, media_geral_2023 = calcular_media_execucao_por_dia(
                tabela, 2023
            )

            media_execucao_2024, media_geral_2024 = calcular_media_execucao_por_dia(
                tabela, 2024
            )
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    '<p style="font-size: 26px; color: #f9f9f9;"><strong>Média de Execução por Dia em Junho de 2024</strong></p>',
                    unsafe_allow_html=True,
                )
                chart = (
                    alt.Chart(media_execucao_junho_2024)
                    .mark_line(color="#1E90FF")
                    .encode(x="DATA FINALIZADO:T", y="MEDIA_EXECUCAO:Q")
                    .properties(width=600, height=400)
                )
                st.altair_chart(chart, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(
                    '<p style="font-size: 18px; color: #f9f9f9;"><strong>Média Geral Junho 2024</strong></p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p style="font-size: 24px; color: #1E90FF;"><strong>{media_geral_junho_2024:.2f}</strong></p>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(
                    '<p style="font-size: 18px; color:  #f9f9f9;"><strong>Média Geral 2023</strong></p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p style="font-size: 24px; color: #1E90FF;"><strong>{media_geral_2023:.2f}</strong></p>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(
                    '<p style="font-size: 18px; color:#f9f9f9;"><strong>Média Geral 2024</strong></p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p style="font-size: 24px; color: #1E90FF;"><strong>{media_geral_2024:.2f}</strong></p>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.write("---")

        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            disciplinas = tabela["DISCIPLINAS"].unique().tolist()
            disciplinas.insert(0, "Todas as disciplinas")
            disciplina_selecionada = st.selectbox(
                "Selecione a disciplina", disciplinas, key="disciplina_selecionada2"
            )

            inicio_data = st.date_input(
                "Data Inicial", value=pd.to_datetime("2023-01-01"), key="data_inicial3"
            )
            fim_data = st.date_input(
                "Data Final", value=pd.to_datetime("2024-12-31"), key="data_final3"
            )

            if disciplina_selecionada != "Todas as disciplinas":
                tabela = tabela[tabela["DISCIPLINAS"] == disciplina_selecionada]

            tabela = tabela[
                (
                    tabela["DATA FINALIZADO"] >= pd.to_datetime(inicio_data)
                ) & (
                    tabela["DATA FINALIZADO"] <= pd.to_datetime(fim_data)
                )
            ]

            os_finalizadas_por_dia = (
                tabela.groupby(pd.to_datetime(tabela["DATA FINALIZADO"]).dt.date)
                .size()
                .reset_index(name="Quantidade")
            )

            total_os_finalizadas = os_finalizadas_por_dia["Quantidade"].sum()

        with col2:
            st.subheader(f"OS Finalizadas por Dia - {disciplina_selecionada}")
            chart = (
                alt.Chart(os_finalizadas_por_dia)
                .mark_bar(color="#FF0000")
                .encode(x="DATA FINALIZADO:T", y="Quantidade:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart, use_container_width=True)

        with col3:
            st.markdown(
                '<p style="font-size: 18px; color: #f9f9f9;"><strong>Total Finalizadas</strong></p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="font-size: 28px; color: #1E90FF;"><strong>{total_os_finalizadas}</strong></p>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        st.write("---")

        tabela_filtrada = tabela[
            [
                "OS",
                "DATA RECEBIDO",
                "DATA FINALIZADO",
                "DISCIPLINAS",
                "RESPONSAVEL TÉCNICO",
            ]
        ]

        os_por_dia = (
            tabela.groupby("DATA FINALIZADO")
            .size()
            .reset_index(name="TOTAL DE OS DO DIA")
        )
        tabela_completa = pd.merge(tabela_filtrada, os_por_dia, on="DATA FINALIZADO")

        col4, col5, col6 = st.columns([4, 3, 1])

        with col4:
            st.subheader("Tabela de OS Finalizadas")
            st.dataframe(tabela_completa)

        junho_2024_finalizado = tabela[
            (tabela["DATA FINALIZADO"].dt.month == 6) & (tabela["DATA FINALIZADO"].dt.year == 2024)
        ]

        junho_2024_finalizado["DATA FINALIZADO"] = pd.to_datetime(
            junho_2024_finalizado["DATA FINALIZADO"]
        ).dt.strftime("%d/%m/%Y")

        os_finalizado_por_dia = (
            junho_2024_finalizado.groupby("DATA FINALIZADO")
            .size()
            .reset_index(name="QUANTIDADE")
        )

        media_execucao_por_dia = (
            os_finalizado_por_dia.groupby("DATA FINALIZADO")["QUANTIDADE"]
            .mean()
            .reset_index(name="MEDIA_EXECUCAO")
        )

        media_geral_junho_2024 = media_execucao_por_dia["MEDIA_EXECUCAO"].mean()

        with col5:
            st.markdown(
                '<p style="font-size: 20px; color: #f9f9f9;"><strong>Média de Execução por Dia em Junho de 2024</strong></p>',
                unsafe_allow_html=True,
            )
            chart = (
                alt.Chart(media_execucao_por_dia)
                .mark_line(color="#1E90FF")
                .encode(x="DATA FINALIZADO:T", y="MEDIA_EXECUCAO:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col6:
            st.markdown(
                '<p style="font-size: 18px; color: #f9f9f9;"><strong>Média Geral</strong></p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="font-size: 36px; color: #1E90FF;"><strong>{media_geral_junho_2024:.2f}</strong></p>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("---")

        tabela["DATA ORÇADO"] = pd.to_datetime(
            tabela["DATA ORÇADO"], dayfirst=True, errors="coerce"
        )
        dados_filtrados = tabela[tabela["DATA ORÇADO"].dt.year.isin([2023, 2024, 2025])]

        col1, col2, col3 = st.columns([1, 5, 1])

        with col1:
            st.write("Filtro 1")
            anos = [2023, 2024, 2025]
            ano_selecionado = st.selectbox(
                "Selecione o Ano", ["Todos"] + anos, key="ano1"
            )

            meses = list(range(1, 13))
            mes_inicial = st.selectbox(
                "Mês Inicial", ["Todos"] + meses, 0, key="mes_inicial1"
            )
            mes_final = st.selectbox(
                "Mês Final", ["Todos"] + meses, 11, key="mes_final1"
            )

        with col2:
            if ano_selecionado != "Todos":
                dados_selecionados = dados_filtrados[
                    dados_filtrados["DATA ORÇADO"].dt.year == ano_selecionado
                ]
            else:
                dados_selecionados = dados_filtrados

            if mes_inicial != "Todos" and mes_final != "Todos":
                inicio_data = pd.Timestamp(
                    year=int(ano_selecionado) if ano_selecionado != "Todos" else 2023,
                    month=int(mes_inicial),
                    day=1,
                )
                fim_data = pd.Timestamp(
                    year=int(ano_selecionado) if ano_selecionado != "Todos" else 2025,
                    month=int(mes_final),
                    day=calendar.monthrange(
                        int(ano_selecionado) if ano_selecionado != "Todos" else 2025,
                        int(mes_final),
                    )[1],
                )
                dados_selecionados = dados_selecionados[
                    (dados_selecionados["DATA ORÇADO"] >= inicio_data)
                    & (dados_selecionados["DATA ORÇADO"] <= fim_data)
                ]

            orcamentos_por_mes = (
                dados_selecionados.groupby(
                    dados_selecionados["DATA ORÇADO"].dt.to_period("M")
                )
                .size()
                .reset_index(name="Quantidade")
            )

            st.markdown(
                f'<p><strong>Quantidade de Orçamentos por Mês (<span style="color: #1E90FF;font-size: 18px">{mes_inicial}/{ano_selecionado} a {mes_final}/{ano_selecionado}</span>)</strong></p>',
                unsafe_allow_html=True,
            )
            orcamentos_por_mes["MES"] = orcamentos_por_mes["DATA ORÇADO"].dt.strftime(
                "%b %Y"
            )
            chart = (
                alt.Chart(orcamentos_por_mes)
                .mark_bar(color="#FF0000")
                .encode(x="MES:T", y="Quantidade:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart, use_container_width=True)
            st.write("---")

        with col3:
            total_orcamentos_mes = dados_selecionados.shape[0]
            total_orcamentos_ano = (
                dados_filtrados[
                    dados_filtrados["DATA ORÇADO"].dt.year == ano_selecionado
                ].shape[0]
                if ano_selecionado != "Todos"
                else dados_filtrados.shape[0]
            )

            st.markdown(
                f"""
                    <p style="font-size: 18px; color:#f9f9f9;"><strong>Total no Mês</strong></p>
                    <p style="font-size: 28px; color: #1E90FF;"><strong>{total_orcamentos_mes}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                    <p style="font-size: 18px; color: #f9f9f9;"><strong>Total no Ano</strong></p>
                    <p style="font-size: 28px; color: #1E90FF;"><strong>{total_orcamentos_ano}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        col6, col7 = st.columns([1, 4])

        with col6:
            st.write("Filtro 3")
            orcamentistas = tabela["ORÇAMENTISTA"].unique().tolist()
            orcamentista_selecionado = st.selectbox(
                "Selecione o Orçamentista",
                ["Todos"] + orcamentistas,
                key="orcamentista1",
            )

            data_inicial = st.date_input(
                "Data Inicial", value=pd.to_datetime("2023-01-01"), key="data_inicial"
            )
            data_final = st.date_input(
                "Data Final", value=pd.to_datetime("2024-12-31"), key="data_final"
            )

        with col7:
            dados_selecionados_3 = tabela.copy()

            if orcamentista_selecionado != "Todos":
                dados_selecionados_3 = dados_selecionados_3[
                    dados_selecionados_3["ORÇAMENTISTA"] == orcamentista_selecionado
                ]

            dados_selecionados_3 = dados_selecionados_3[
                (dados_selecionados_3["DATA ORÇADO"] >= pd.to_datetime(data_inicial))
                & (dados_selecionados_3["DATA ORÇADO"] <= pd.to_datetime(data_final))
            ]

            orcamentos_por_dia = (
                dados_selecionados_3.groupby(
                    dados_selecionados_3["DATA ORÇADO"].dt.to_period("D")
                )
                .size()
                .reset_index(name="Quantidade")
            )
            orcamentos_por_dia["DATA"] = orcamentos_por_dia["DATA ORÇADO"].dt.strftime(
                "%d/%m/%Y"
            )

            st.subheader("Quantidade de Orçamentos por Orçamentista")
            chart_3 = (
                alt.Chart(orcamentos_por_dia)
                .mark_bar(color="#1E90FF")
                .encode(x="DATA:T", y="Quantidade:Q")
                .properties(width=600, height=400)
            )
            st.altair_chart(chart_3, use_container_width=True)

        col8, col9, col10 = st.columns(3)

        with col8:
            total_orcamentos_mes_orcamentista = orcamentos_por_dia["Quantidade"].sum()
            st.markdown(
                f"""
                    <p style="font-size: 18px; color: #f9f9f9;"><strong>Total no Mês</strong></p>
                    <p style="font-size: 24px; color: #1E90FF;"><strong>{total_orcamentos_mes_orcamentista}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col9:
            total_orcamentos_dia_orcamentista = orcamentos_por_dia["Quantidade"].sum()
            st.markdown(
                f"""
                    <p style="font-size: 18px; color: #f9f9f9;"><strong>Total no Dia</strong></p>
                    <p style="font-size: 24px; color: #1E90FF;"><strong>{total_orcamentos_dia_orcamentista}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.write("-----")
    except pd.errors.EmptyDataError:
        st.error("O arquivo CSV está vazio.")
    except pd.errors.ParserError:
        st.error("Erro ao analisar o arquivo CSV.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo CSV: {e}")


if __name__ == "__main__":
    gerar_contrato()
