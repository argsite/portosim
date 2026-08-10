import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard de Mortalidade - Porto Feliz", layout="wide")

st.title("📊 Painel Estratégico de Monitoramento de Mortalidade - Porto Feliz")
st.markdown("Ferramenta avançada de apoio ao planejamento em Saúde da Família.")

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("sim_porto_feliz_2020_2025.csv")
    return df

df = carregar_dados()

# Tratamento básico da idade no SIM (se a coluna existir)
def converter_idade(val):
    try:
        val_str = str(val).zfill(4)
        tipo = val_str[0]
        idade_num = int(val_str[1:])
        if tipo == '4': # Anos completos
            return idade_num
        elif tipo == '5': # 100 anos ou mais
            return 100 + idade_num
        else:
            return 0 # Ignora menores de 1 ano para esta métrica simples
    except:
        return None

if "IDADE" in df.columns and "IDADE_ANOS" not in df.columns:
    df["IDADE_ANOS"] = df["IDADE"].apply(converter_idade)

# Barra Lateral - Filtros
st.sidebar.header("🔍 Filtros Operacionais")
anos_disponiveis = sorted(df["ANO_OBITO"].dropna().unique())
anos_selecionados = st.sidebar.multiselect("Selecione o(s) Ano(s):", options=anos_disponiveis, default=anos_disponiveis)

df_filtrado = df[df["ANO_OBITO"].isin(anos_selecionados)] if anos_selecionados else df.copy()

# Métricas Principais
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de Óbitos", len(df_filtrado))
c2.metric("Anos Analisados", f"{len(anos_selecionados)}")
if "IDADE_ANOS" in df_filtrado.columns and not df_filtrado["IDADE_ANOS"].dropna().empty:
    media_idade = int(df_filtrado["IDADE_ANOS"].mean())
    c3.metric("Média de Idade no Óbito", f"{media_idade} anos")
c4.metric("Município", "Porto Feliz - SP")
st.markdown("---")

# Abas para Organizar o Dashboard
aba1, aba2, aba3 = st.tabs(["📈 Visão Geral & Tendências", "👥 Perfil Demográfico & Local", "🔬 Causas Detalhadas"])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Evolução Anual dos Óbitos")
        obitos_ano = df_filtrado["ANO_OBITO"].value_counts().sort_index().reset_index()
        obitos_ano.columns = ["Ano", "Total"]
        fig_ano = px.bar(obitos_ano, x="Ano", y="Total", text="Total", color="Total", color_continuous_scale="Blues")
        st.plotly_chart(fig_ano, use_container_width=True)
        
    with col2:
        st.subheader("📅 Sazonalidade (Óbitos por Mês)")
        if "DTOBITO" in df_filtrado.columns:
            # Extrai o mês da data do óbito (formato ddmmyyyy no SIM)
            df_filtrado["MES"] = df_filtrado["DTOBITO"].astype(str).str.zfill(8).str[2:4]
            obitos_mes = df_filtrado["MES"].value_counts().sort_index().reset_index()
            obitos_mes.columns = ["Mês", "Total"]
            meses_nomes = {"01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr", "05": "Mai", "06": "Jun", 
                           "07": "Jul", "08": "Ago", "09": "Set", "10": "Out", "11": "Nov", "12": "Dez"}
            obitos_mes["Mês"] = obitos_mes["Mês"].map(meses_nomes)
            fig_mes = px.line(obitos_mes, x="Mês", y="Total", markers=True, line_shape="spline")
            st.plotly_chart(fig_mes, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏥 Local de Ocorrência")
        if "LOCAL" in df_filtrado.columns:
            # Legenda amigável para o campo LOCAL do SIM
            mapa_local = {1: "Hospital", 2: "Outro Estab. Saúde", 3: "Domicílio", 4: "Via Pública", 5: "Outros"}
            df_filtrado["LOCAL_DESC"] = df_filtrado["LOCAL"].map(mapa_local).fillna("Não Informado")
            locais = df_filtrado["LOCAL_DESC"].value_counts().reset_index()
            locais.columns = ["Local", "Quantidade"]
            fig_local = px.pie(locais, names="Local", values="Quantidade", hole=0.4)
            st.plotly_chart(fig_local, use_container_width=True)
            
    with col2:
        st.subheader("👥 Distribuição por Faixa Etária")
        if "IDADE_ANOS" in df_filtrado.columns:
            bins = [0, 19, 39, 59, 79, 120]
            labels = ["0-19 anos", "20-39 anos", "40-59 anos", "60-79 anos", "80+ anos"]
            df_filtrado["FAIXA_ETARIA"] = pd.cut(df_filtrado["IDADE_ANOS"], bins=bins, labels=labels, right=False)
            faixas = df_filtrado["FAIXA_ETARIA"].value_counts().sort_index().reset_index()
            faixas.columns = ["Faixa Etária", "Total"]
            fig_idade = px.bar(faixas, x="Faixa Etária", y="Total", color="Total", color_continuous_scale="Purples")
            st.plotly_chart(fig_idade, use_container_width=True)

with aba3:
    st.subheader("🔬 Principais Causas Básicas (CID-10)")
    if "CAUSABAS" in df_filtrado.columns:
        top_causas = df_filtrado["CAUSABAS"].value_counts().head(12).reset_index()
        top_causas.columns = ["CID-10", "Ocorrências"]
        fig_causa = px.bar(top_causas, x="Ocorrências", y="CID-10", orientation="h", color="Ocorrências", color_continuous_scale="Reds")
        fig_causa.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_causa, use_container_width=True)

# Expander com os dados brutos
with st.expander("📋 Ver base de dados detalhada e limpa"):
    st.dataframe(df_filtrado)
