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

# Dicionário de Tradução das Principais CID-10 de Óbito
dicionario_cid = {
    "I10": "Hipertensão essencial (primária)",
    "I21": "Infarto agudo do miocárdio",
    "I50": "Insuficiência cardíaca",
    "I64": "Acidente vascular cerebral (AVC) não especificado",
    "I63": "Infarto cerebral",
    "C349": "Neoplasia maligna dos brônquios ou pulmões",
    "C509": "Neoplasia maligna da mama",
    "C61": "Neoplasia maligna da próstata",
    "C189": "Neoplasia maligna do cólon",
    "C259": "Neoplasia maligna do pâncreas",
    "J189": "Pneumonia não especificada",
    "J180": "Broncopneumonia não especificada",
    "J449": "Doença pulmonar obstrutiva crônica (DPOC)",
    "J690": "Pneumonite devida a alimentos e vômitos",
    "B342": "Infecção por coronavírus (Covid-19)",
    "A419": "Septicemia não especificada",
    "R092": "Parada respiratória",
    "R99": "Outras causas mal definidas",
    "X700": "Lesão autoprovocada (Suicídio)",
    "V892": "Acidente de transporte",
}

def traduzir_cid(codigo):
    if pd.isna(codigo):
        return "Não Informado"
    codigo_limpo = str(codigo).strip().upper()
    return dicionario_cid.get(codigo_limpo, f"Outra causa ({codigo_limpo})")

if "CAUSABAS" in df.columns:
    df["CAUSA_DESC"] = df["CAUSABAS"].apply(traduzir_cid)

# Conversão robusta de idade
def converter_idade_sim(val):
    try:
        val_str = str(int(val)).zfill(3)
        tipo = val_str[0]
        valor = int(val_str[1:])
        if tipo == '4':
            return valor
        elif tipo == '5':
            return 100 + valor
        elif tipo in ['1', '2', '3']:
            return 0
        return None
    except:
        return None

if "IDADE" in df.columns and "IDADE_ANOS" not in df.columns:
    df["IDADE_ANOS"] = df["IDADE"].apply(converter_idade_sim)

# Criação da Faixa Etária para filtros
bins = [0, 20, 40, 60, 80, 130]
labels = ["0-19 anos", "20-39 anos", "40-59 anos", "60-79 anos", "80+ anos"]
df["FAIXA_ETARIA"] = pd.cut(df["IDADE_ANOS"], bins=bins, labels=labels, right=False)

# Mapeamento do Local de Óbito
mapa_local = {1: "Hospital", 2: "Outro Estab. Saúde", 3: "Domicílio", 4: "Via Pública", 5: "Outros"}
df["LOCAL_DESC"] = df["LOCAL"].map(mapa_local).fillna("Não Informado")

# Barra Lateral - Filtros Globais
st.sidebar.header("🔍 Filtros Operacionais Globais")
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
aba1, aba2, aba3, aba4 = st.tabs(["📈 Visão Geral", "👥 Perfil & Local", "🔬 Causas", "📋 Tabela Interativa & Filtros"])

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
        locais = df_filtrado["LOCAL_DESC"].value_counts().reset_index()
        locais.columns = ["Local", "Quantidade"]
        fig_local = px.pie(locais, names="Local", values="Quantidade", hole=0.4)
        st.plotly_chart(fig_local, use_container_width=True)
            
    with col2:
        st.subheader("👥 Distribuição por Faixa Etária")
        faixas = df_filtrado["FAIXA_ETARIA"].value_counts().sort_index().reset_index()
        faixas.columns = ["Faixa Etária", "Total"]
        fig_idade = px.bar(faixas, x="Faixa Etária", y="Total", color="Total", color_continuous_scale="Purples", text="Total")
        st.plotly_chart(fig_idade, use_container_width=True)

with aba3:
    st.subheader("🔬 Principais Causas de Óbito (Clínicas)")
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
        cruzamento_ano_causa, x="ANO_OBITO", y="Quantidade", color="CAUSA_DESC", barmode="group",
        title="Evolução das 5 Principais Causas de Óbito por Ano"
    )
    st.plotly_chart(fig_cruzamento, use_container_width=True)

with aba4:
    st.subheader("📋 Tabela de Consulta Detalhada com Filtros Dinâmicos")
    st.markdown("Use os menus abaixo para filtrar especificamente os registros que deseja analisar ou exportar para a equipe.")
    
    # Menus suspensos para filtragem fina na tabela
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        faixas_disponiveis = df_filtrado["FAIXA_ETARIA"].dropna().unique().astype(str)
        faixa_filtro = st.multiselect("Filtrar por Faixa Etária:", options=sorted(faixas_disponiveis))
        
    with col_f2:
        causas_disponiveis = df_filtrado["CAUSA_DESC"].dropna().unique()
        causa_filtro = st.multiselect("Filtrar por Causa de Morte:", options=sorted(causas_disponiveis))
        
    with col_f3:
        locais_disponiveis = df_filtrado["LOCAL_DESC"].dropna().unique()
        local_filtro = st.multiselect("Filtrar por Local de Óbito:", options=sorted(locais_disponiveis))
        
    # Aplicação dos filtros locais da tabela
    df_tabela = df_filtrado.copy()
    if faixa_filtro:
        df_tabela = df_tabela[df_tabela["FAIXA_ETARIA"].astype(str).isin(faixa_filtro)]
    if causa_filtro:
        df_tabela = df_tabela[df_tabela["CAUSA_DESC"].isin(causa_filtro)]
    if local_filtro:
        df_tabela = df_tabela[df_tabela["LOCAL_DESC"].isin(local_filtro)]
        
    st.markdown(f"**Registros encontrados com os filtros aplicados:** {len(df_tabela)}")
    
    # Seleção de colunas mais limpas para exibição amigável
    colunas_exibicao = ["ANO_OBITO", "DTOBITO", "IDADE_ANOS", "FAIXA_ETARIA", "SEXO", "CAUSA_DESC", "LOCAL_DESC"]
    colunas_presentes = [c for c in colunas_exibicao if c in df_tabela.columns]
    
    st.dataframe(df_tabela[colunas_presentes], use_container_width=True)
    
    # Botão para download dos dados filtrados em CSV
    csv_dados = df_tabela[colunas_presentes].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados filtrados em CSV (para relatório)",
        data=csv_dados,
        file_name="obitos_porto_feliz_filtrado.csv",
        mime="text/csv",
    )
