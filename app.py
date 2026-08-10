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

# Dicionário de Tradução das Principais CID-10 de Óbito (Capítulos e Códigos Comuns)
dicionario_cid = {
    # Doenças do aparelho circulatório
    "I10": "Hipertensão essencial (primária)",
    "I21": "Infarto agudo do miocárdio",
    "I50": "Insuficiência cardíaca",
    "I64": "Acidente vascular cerebral (AVC) não especificado",
    "I63": "Infarto cerebral",
    # Neoplasias (Tumores)
    "C349": "Neoplasia maligna dos brônquios ou pulmoões",
    "C509": "Neoplasia maligna da mama",
    "C61": "Neoplasia maligna da próstata",
    "C189": "Neoplasia maligna do cólon",
    "C259": "Neoplasia maligna do pâncreas",
    # Doenças respiratórias
    "J189": "Pneumonia não especificada",
    "J180": "Broncopneumonia não especificada",
    "J449": "Doença pulmonar obstrutiva crônica (DPOC)",
    "J690": "Pneumonite devida a alimentos e vômitos",
    # Infecções e Outros
    "B342": "Infecção por coronavírus de localização não especificada (Covid-19)",
    "A419": "Septicemia não especificada",
    "R092": "Parada respiratória",
    "R99": "Outras causas mal definidas e desconhecidas",
    # Causas Externas
    "X700": "Lesão autoprovocada intencionalmente (Suicídio)",
    "V892": "Acidente de transporte não especificado",
    "X990": "Agressão por objeto cortante"
}

def traduzir_cid(codigo):
    if pd.isna(codigo):
        return "Não Informado"
    codigo_limpo = str(codigo).strip().upper()
    # Retorna a descrição amigável se existir no dicionário, senão exibe o próprio código formatado
    return dicionario_cid.get(codigo_limpo, f"Outra causa ({codigo_limpo})")

# Aplica a tradução das causas
if "CAUSABAS" in df.columns:
    df["CAUSA_DESC"] = df["CAUSABAS"].apply(traduzir_cid)

# Correção da conversão de idade do padrão SIM do DATASUS
def converter_idade_sim(val):
    try:
        val_str = str(int(val)).zfill(3)
        tipo = val_str[0]
        valor = int(val_str[1:])
        if tipo == '4':  # Anos completos
            return valor
        elif tipo == '5':  # 100 anos ou mais
            return 100 + valor
        elif tipo in ['1', '2', '3']:  # Menor de 1 ano
            return 0
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
        st.subheader("👥 Distribuição por Faixa Etária")
        if "IDADE_ANOS" in df_filtrado.columns:
            bins = [0, 20, 40, 60, 80, 130]
            labels = ["0-19 anos", "20-39 anos", "40-59 anos", "60-79 anos", "80+ anos"]
            df_filtrado["FAIXA_ETARIA"] = pd.cut(df_filtrado["IDADE_ANOS"], bins=bins, labels=labels, right=False)
            faixas = df_filtrado["FAIXA_ETARIA"].value_counts().sort_index().reset_index()
            faixas.columns = ["Faixa Etária", "Total"]
            fig_idade = px.bar(faixas, x="Faixa Etária", y="Total", color="Total", color_continuous_scale="Purples", text="Total")
            st.plotly_chart(fig_idade, use_container_width=True)

with aba3:
    st.subheader("🔬 Principais Causas de Óbito (Clínicas)")
    if "CAUSA_DESC" in df_filtrado.columns:
        top_causas = df_filtrado["CAUSA_DESC"].value_counts().head(10).reset_index()
        top_causas.columns = ["Causa", "Ocorrências"]
        fig_causa = px.bar(top_causas, x="Ocorrências", y="Causa", orientation="h", color="Ocorrências", color_continuous_scale="Reds", text="Ocorrências")
        fig_causa.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_causa, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Cruzamento: Principais Causas por Ano")
        top_causas_lista = df_filtrado["CAUSA_DESC"].value_counts().head(5).index.tolist()
        df_cruzamento = df_filtrado[df_filtrado["CAUSA_DESC"].isin(top_causas_lista)]
        
        cruzamento_ano_causa = df_cruzamento.groupby(["ANO_OBITO", "CAUSA_DESC"]).size().reset_index(name="Quantidade")
        fig_cruzamento = px.bar(
            cruzamento_ano_causa, 
            x="ANO_OBITO", 
            y="Quantidade", 
            color="CAUSA_DESC", 
            barmode="group",
            title="Evolução das 5 Principais Causas de Óbito por Ano"
        )
        st.plotly_chart(fig_cruzamento, use_container_width=True)

# Expander com os dados brutos
with st.expander("📋 Ver base de dados detalhada e limpa"):
    st.dataframe(df_filtrado)
