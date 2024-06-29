import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.express as px

# Constantes
SHEET_NAME = "Paradas"
SHEET_NAME1 = "Solicitações_Engeman"
uploaded_file = ""

# mostrar em tela cheia
st.set_page_config(layout="wide")

# Função para carregar planilha


def load_data(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)

# Função para preparar dados


def prepare_data(df):
    df["Recebimento"] = df["Recebimento"].map({1: "REC 01", 2: "REC 02"})
    df['TempoParada'] = df['DataFimParada'] - df['DataInicioParada']
    df["Data"] = df['DataInicioParada'].dt.date
    return df

# Função para preparar dados engeman


def prepara_data_engeman(df):
    df["Data"] = df['Data'].dt.date
    df["setor"] = df["TAG"].str.split("-").str[1]
    return df

# Função Filtro


def filter(df, st):
    st.sidebar.subheader("Selecione um intervalo de datas:")
    start_date = st.sidebar.date_input('Select a start date:', value=df['Data'].min(
    ), min_value=df['Data'].min(), max_value=df['Data'].max())
    end_date = st.sidebar.date_input('Select a end date:', value=df['Data'].max(
    ), min_value=start_date, max_value=df['Data'].max())
    st.sidebar.subheader("Selecione os setores desejados:")
    setor = st.sidebar.multiselect("Entre com os setores", df['SetorCausador'].unique(), [
                                   "Automacao", "Eletrica", "Mecanica"])
    df_filtered = df.query(
        "Data >= @start_date and Data <= @end_date and SetorCausador == @setor")
    return df_filtered, start_date, end_date, setor

# Gráfico 1


def grafico_1(df_filtered):
    tempo_parada = df_filtered.groupby(["NomeParada", "Recebimento", "SetorCausador"])[
        ["TempoParada", "SegundosAux"]].sum().reset_index()

    tempo_parada["Horas"] = tempo_parada["SegundosAux"].apply(
        lambda x: str(timedelta(seconds=x)))

    fig = px.treemap(tempo_parada,
                     values="SegundosAux",
                     path=["Recebimento", "NomeParada"],
                     color="SetorCausador",
                     hover_data=["Horas", "SetorCausador"],
                     title="TreeMap Paradas"
                     )
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 2


def grafico_2(df_filtered):
    tipo_parada = df_filtered.groupby(["TipoParada"])[
        "Recebimento"].value_counts().reset_index()

    fig_tipo_parada = px.bar(tipo_parada,
                             x="TipoParada",
                             y="count",
                             title="Tipo de Paradas",
                             color="Recebimento",
                             text_auto="count"
                             )
    st.plotly_chart(fig_tipo_parada, use_container_width=True)

# grafico 3


def grafico_3(df_filtered):
    qtd_parada = df_filtered.groupby(["Supervisor"])[
        "Recebimento"].value_counts().reset_index()

    qtd = qtd_parada['count'].sum()

    fig_qtd_parada = px.pie(qtd_parada, names="Supervisor",
                            values="count",
                            title=f"Qdt Paradas em Turnos - {qtd}"
                            )
    st.plotly_chart(fig_qtd_parada, use_container_width=True)

# grafico 4


def grafico_4(df_filtered):
    qtd_parada_area = df_filtered.groupby(["Area"])[
        "Recebimento"].value_counts().reset_index()

    qtd_parada_area = qtd_parada_area.sort_values("count")

    fig_qtd_parada_area = px.bar(qtd_parada_area, x="Area",
                                 y="count",
                                 title="Qdt Paradas por Area",
                                 color="Recebimento",
                                 text_auto="count"
                                 )
    st.plotly_chart(fig_qtd_parada_area, use_container_width=True)

# grafico 5


def grafico_5(df_filtered):
    setor = df_filtered.groupby(["SetorCausador"])[
        "Recebimento"].value_counts().reset_index()

    setor = setor.sort_values("count")

    fig_setor = px.bar(setor, x="SetorCausador",
                       y="count",
                       title="Qtd de Paradas por Setor",
                       color="Recebimento",
                       text_auto="count",
                       )
    st.plotly_chart(fig_setor, use_container_width=True)

# grafico 6


def grafico_6(df_filtered):
    tempo = df_filtered.groupby(["SetorCausador", "Recebimento"])[
        "SegundosAux"].sum().reset_index()

    tempo["Horas"] = tempo["SegundosAux"].apply(
        lambda x: str(timedelta(seconds=x)))

    tempo = tempo.sort_values("SegundosAux")

    fig_tempo = px.bar(tempo, y="SetorCausador",
                       x="SegundosAux",
                       title="Tempo de Paradas por Setor",
                       color="Recebimento",
                       hover_data="Horas",
                       orientation="h"
                       )
    st.plotly_chart(fig_tempo, use_container_width=True)

# Função principal


def main():

    # Carregar planilha
    df = load_data(uploaded_file, SHEET_NAME)
    df_engeman = load_data(uploaded_file, SHEET_NAME1)

    # Preparar dados
    df = prepare_data(df)
    df_engeman = prepara_data_engeman(df_engeman)

    # Mostrar logo na sidebar
    st.sidebar.write("By Diogo Daniel")

    # Aplicar filtro
    df_filtered, start_date, end_date, setor = filter(df, st)
    qtd = df_filtered["NomeParada"].count()

    # Qtde engeman
    df_engeman = df_engeman.query(
        "Data >= @start_date and Data <= @end_date and (setor == 'RC01' or setor == 'UB02' or setor == 'RC02' or setor == 'DB01' or setor == 'RG01')")
    qtde = df_engeman["Data"].count()

    # Titulo da pagina
    st.title("Daily Report Winter 24' - Stop Control")
    # Texto
    st.subheader(
        f"Data inicial: :blue[{start_date}] - Data final: :blue[{end_date}]")

    # Subtitulo
    st.subheader("KPI's Paradas", divider="rainbow")

    grafico_1(df_filtered)

    col1, col2 = st.columns(2)
    col3, col4, col5 = st.columns(3)

    with col1:
        grafico_5(df_filtered)
    with col2:
        grafico_6(df_filtered)
    with col3:
        grafico_4(df_filtered)
    with col4:
        grafico_3(df_filtered)
    with col5:
        grafico_2(df_filtered)

    return df_filtered, df_engeman, qtd, qtde


def upload():
    st.title("Upload de Arquivo")

    # Permite o usuário fazer upload de um arquivo
    uploaded_file = st.file_uploader("Escolha um arquivo EXCEL", type="xlsx")

    if uploaded_file is not None:
        # Carregar o arquivo para um DataFrame do pandas
        arquivo = pd.read_excel(uploaded_file)

    return uploaded_file


# Menu de opções
carregar_dados, graficos, tabelas, quebras_maquinas, incompatibilidade = st.tabs(
    ["Carregar Planilha", "KPI's", "Tabelas", "Quebra de Maquinas", "Incompatibilidade"])

try:

    # opção 1
    with carregar_dados:
        uploaded_file = upload()

    # opção 2
    with graficos:
        df_filtered, df_engeman, qtd, qtde = main()

    # opção 3
    with tabelas:
        # Subtitulo
        st.subheader("Fonte: Banco de Dados | Tablet")
        st.dataframe(df_filtered)

        # Subtitulo
        st.subheader("Fonte: SoftWare Engeman")
        st.dataframe(df_engeman)

        # Barra de expansão
        with st.expander("Veja qtd de solicitações no engeman:"):
            st.write(f"Quantidade de solicitações serviço: {qtde}")
            st.write(f"Quantidade de paradas na produção: {qtd}")

    # opção 4
    with quebras_maquinas:
        pass

    # opção 5
    with incompatibilidade:
        pass


except Exception as e:
    st.write("Faça upload de um arquivo com nome de: ControldeParadas")
    st.write(e)
