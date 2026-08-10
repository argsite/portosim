import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página para o modo largo (wide)
st.set_page_config(page_title="Dashboard de Mortalidade - Porto Feliz", layout="wide")

# Título principal do painel
st.title("📊 Painel de Monitoramento de Mortalidade - Porto Feliz (SIM)")
st.markdown("Ferramenta de apoio para a gestão e planejamento das equipes de Saúde da Família.")

# Carregamento dos dados com cache para otimizar
@st.cache_data
def carregar_dados():
    df = pd.read_csv("sim_porto_feliz_2020_2025.csv")
    return df

df = carregar_dados()

# Barra Lateral (Sidebar) para Filtros
st.sidebar.header("🔍 Filtros Operacionais")

# Filtro de Anos
anos_disponiveis = sorted(df["ANO_OBITO"].dropna().unique())
anos_selecionados = st.sidebar.multiselect("Selecione o(s) Ano(s):", options=anos_disponiveis, default=anos_disponiveis)

# Aplicando o filtro de ano no DataFrame
if anos_selecionados:
    df_filtrado = df[df["ANO_OBITO"].isin(anos_selecionados)]
else:
    df_filtrado = df.copy()

# Métricas Resumidas no Topo
st.markdown("---")
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="Total de Óbitos no Período", value=len(df_filtrado))
with col_m2:
    if "IDADE" in df_filtrado.columns:
        # A idade no SIM vem codificada (ex: 4xx para anos, onde xx é a idade). 
        # Vamos usar uma média simples ou contagem se o formato for numérico padrão.
        st.metric(label="Anos Selecionados", value=f"{len(anos_selecionados)} ano(s)")
with col_m3:
    st.metric(label="Município", value="Porto Feliz - SP")
st.markdown("---")

# Layout de Gráficos em Colunas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Óbitos por Ano")
    if "ANO_OBITO" in df_filtrado.columns:
        obitos_ano = df_filtrado["ANO_OBITO"].value_counts().sort_index().reset_index()
        obitos_ano.columns = ["Ano", "Total de Óbitos"]
        fig_ano = px.bar(obitos_ano, x="Ano", y="Total de Óbitos", text="Total de Óbitos", color="Total de Óbitos", color_continuous_scale="Blues")
        st.plotly_chart(fig_ano, use_container_width=True)

with col2:
    st.subheader("🏥 Local de Ocorrência do Óbito")
    if "LOCAL" in df_filtrado.columns:
        # O campo LOCAL costuma vir em códigos (1-Hospital, 2-Outro estab, 3-Domicílio, etc.)
        locais_contagem = df_filtrado["LOCAL"].value_counts().reset_index()
        locais_contagem.columns = ["Local", "Quantidade"]
        fig_local = px.pie(locais_contagem, names="Local", values="Quantidade", hole=0.4)
        st.plotly_chart(fig_local, use_container_width=True)

# Seção inferior: Causas Básicas (CID-10)
st.subheader("🔬 Principais Causas Básicas de Óbito (Código CID-10)")
if "CAUSABAS" in df_filtrado.columns:
    top_causas = df_filtrado["CAUSABAS"].value_counts().head(10).reset_index()
    top_causas.columns = ["Causa (CID-10)", "Ocorrências"]
    fig_causa = px.bar(top_causas, x="Ocorrências", y="Causa (CID-10)", orientation="h", color="Ocorrências", color_continuous_scale="Reds")
    fig_causa.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_causa, use_container_width=True)

# Tabela detalhada opcional
with st.expander("📋 Visualizar base de dados bruta filtrada"):
    st.dataframe(df_filtrado)
