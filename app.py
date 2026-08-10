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

# Correção robusta da conversão de idade do padrão SIM do DATASUS
def converter_idade_sim(val):
    try:
        val_str = str(int(val)).zfill(3)
        tipo = val_str[0]
        valor = int(val_str[1:])
        if tipo == '4':  # Anos completos (ex: 438 -> 38 anos)
            return valor
        elif tipo == '5':  # 100 anos ou mais (ex: 502 -> 102 anos)
            return 100 + valor
        elif tipo in ['1', '2', '3']:  # Minutos, horas ou dias de vida
            return 0  # Considerado menor de 1 ano
        return None
    except:
        return None

if "IDADE" in df.columns and "IDADE_ANOS" not in df.columns:
    df["IDADE_ANOS"] = df["IDADE"].apply(converter_idade_sim)

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
aba1, aba2, aba3 = st.tabs(["📈 Visão Geral & Tendências", "👥 Perfil Demográfico & Local", "🔬 Causas & Cruzamento Anual"])

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
            df_temp = df_filtrado.copy()
            df_temp["MES"] = df_temp["DTOBITO"].astype(str).str.zfill(8).str[2:4]
            obitos_mes = df_temp["MES"].value_counts().sort_index().reset_index()
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
            mapa_local = {1: "Hospital", 2: "Outro Estab. Saúde", 3: "Domicílio", 4: "Via Pública", 5: "Outros"}
            df_filtrado["LOCAL_DESC"] = df_filtrado["LOCAL"].map(mapa_local).fillna("Não Informado")
            locais = df_filtrado["LOCAL_DESC"].value_counts().reset_index()
            locais.columns = ["Local", "Quantidade"]
            fig_local = px.pie(locais, names="Local", values="Quantidade", hole=0.4)
            st.plotly_chart(fig_local, use_container_width=True)
            
    with col2:
        st.subheader("👥 Distribuição por Faixa Etária Corrigida")
        if "IDADE_ANOS" in df_filtrado.columns:
            bins = [0, 20, 40, 60, 80, 130]
            labels = ["0-19 anos", "20-39 anos", "40-59 anos", "60-79 anos", "80+ anos"]
            df_filtrado["FAIXA_ETARIA"] = pd.cut(df_filtrado["IDADE_ANOS"], bins=bins, labels=labels, right=False)
            faixas = df_filtrado["FAIXA_ETARIA"].value_counts().sort_index().reset_index()
            faixas.columns = ["Faixa Etária", "Total"]
            fig_idade = px.bar(faixas, x="Faixa Etária", y="Total", color="Total", color_continuous_scale="Purples", text="Total")
            st.plotly_chart(fig_idade, use_container_width=True)

with aba3:
    st.subheader("🔬 Principais Causas Básicas (CID-10)")
    if "CAUSABAS" in df_filtrado.columns:
        top_causas = df_filtrado["CAUSABAS"].value_counts().head(10).reset_index()
        top_causas.columns = ["CID-10", "Ocorrências"]
        fig_causa = px.bar(top_causas, x="Ocorrências", y="CID-10", orientation="h", color="Ocorrências", color_continuous_scale="Reds", text="Ocorrências")
        fig_causa.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_causa, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Cruzamento: Causas de Óbito por Ano")
        # Gráfico de barras empilhadas ou agrupadas mostrando a evolução das principais causas ao longo dos anos
        top_cid_lista = df_filtrado["CAUSABAS"].value_counts().head(5).index.tolist()
        df_cruzamento = df_filtrado[df_filtrado["CAUSABAS"].isin(top_cid_lista)]
        
        cruzamento_ano_causa = df_cruzamento.groupby(["ANO_OBITO", "CAUSABAS"]).size().reset_index(name="Quantidade")
        fig_cruzamento = px.bar(
            cruzamento_ano_causa, 
            x="ANO_OBITO", 
            y="Quantidade", 
            color="CAUSABAS", 
            barmode="group",
            title="Evolução das 5 Principais Causas (CID-10) por Ano"
        )
        st.plotly_chart(fig_cruzamento, use_container_width=True)

# Expander com os dados brutos
with st.expander("📋 Ver base de dados detalhada e limpa"):
    st.dataframe(df_filtrado)
