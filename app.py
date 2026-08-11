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

# Dicionário Clínico Abrangente e Ampliado (CID-10)
dicionario_cid = {
    "A09": "Diarreia e gastroenterite de origem infecciosa presumida",
    "A150": "Tuberculose pulmonar",
    "A418": "Outras septicemias",
    "A419": "Septicemia não especificada (Sepse)",
    "A46": "Erisipela",
    "B24": "Doença pelo vírus da imunodeficiência humana [HIV]",
    "B342": "Infecção por coronavírus (Covid-19)",
    "C169": "Neoplasia maligna do estômago",
    "C189": "Neoplasia maligna do cólon",
    "C229": "Neoplasia maligna do fígado, não especificada",
    "C259": "Neoplasia maligna do pâncreas",
    "C349": "Neoplasia maligna dos brônquios ou pulmões",
    "C508": "Neoplasia maligna da mama com lesão com sobreposição",
    "C509": "Neoplasia maligna da mama, não especificada",
    "C539": "Neoplasia maligna do colo do útero, não especificado",
    "C61": "Neoplasia maligna da próstata",
    "C780": "Neoplasia maligna secundária dos pulmões",
    "C80": "Neoplasia maligna, sem especificação de localização",
    "E107": "Diabetes mellitus insulino-dependente com múltiplas complicações",
    "E108": "Diabetes mellitus insulino-dependente com complicações não especificadas",
    "E112": "Diabetes mellitus não insulino-dependente com complicações renais",
    "E118": "Diabetes mellitus não insulino-dependente com complicações não especificadas",
    "E119": "Diabetes mellitus não insulino-dependente sem complicações",
    "E142": "Diabetes mellitus não especificado com complicações renais",
    "E149": "Diabetes mellitus não especificado",
    "E46": "Desnutrição proteico-calórica não especificada",
    "F03": "Demência não especificada",
    "F102": "Transtornos mentais devidos ao uso de álcool - dependência",
    "G301": "Doença de Alzheimer com início tardio",
    "G309": "Doença de Alzheimer não especificada",
    "G934": "Encefalopatia não especificada",
    "I10": "Hipertensão essencial (primária)",
    "I110": "Doença cardíaca hipertensiva com insuficiência cardíaca",
    "I120": "Doença renal hipertensiva com insuficiência renal",
    "I132": "Doença cardíaca e renal hipertensiva com insuficiência cardíaca e renal",
    "I219": "Infarto agudo do miocárdio não especificado",
    "I251": "Doença aterosclerótica do coração",
    "I269": "Embolia pulmonar sem menção de cor pulmonale agudo",
    "I500": "Insuficiência cardíaca congestiva",
    "I509": "Insuficiência cardíaca não especificada",
    "I619": "Hemorragia intracraniana não especificada",
    "I64": "Acidente vascular cerebral (AVC) não especificado",
    "I694": "Sequelas de acidente vascular cerebral não especificado",
    "I698": "Sequelas de outras doenças cerebrovasculares e as não especificadas",
    "I713": "Aneurisma da aorta abdominal, rotundo",
    "J159": "Pneumonia bacteriana não especificada",
    "J180": "Broncopneumonia não especificada",
    "J189": "Pneumonia não especificada",
    "J440": "DPOC com infecção respiratória aguda inferior",
    "J441": "DPOC com exacerbação aguda, não especificada",
    "J448": "Outras formas especificadas de doença pulmonar obstrutiva crônica",
    "J449": "Doença pulmonar obstrutiva crônica (DPOC) não especificada",
    "J690": "Pneumonite devida a alimentos e vômitos (aspiração)",
    "J841": "Outras doenças pulmonares intersticiais fibróticas",
    "J960": "Insuficiência respiratória aguda",
    "J969": "Insuficiência respiratória não especificada",
    "K703": "Cirrose hepática alcoólica",
    "K746": "Outras cirroses hepáticas e as não especificadas",
    "N179": "Insuficiência renal aguda não especificada",
    "N189": "Doença renal crônica não especificada",
    "N390": "Infecção do trato urinário de local não especificado",
    "R570": "Choque cardiogênico",
    "R092": "Parada respiratória",
    "R54": "Senilidade (Velhice extrema)",
    "R961": "Morte ocorrida menos de 24 horas após o início dos sintomas",
    "R98": "Morte sem assistência",
    "R99": "Outras causas mal definidas e desconhecidas",
    "V031": "Pedestre traumatizado em colisão com automóvel, caminhonete ou furgão",
    "V093": "Pedestre traumatizado em outros acidentes de transporte e nos não especificados",
    "V234": "Motociclista traumatizado em colisão com automóvel, caminhonete ou furgão",
    "V892": "Acidente de trânsito não especificado",
    "W010": "Queda no mesmo nível por piso escorregadio",
    "W180": "Outras quedas no mesmo nível",
    "W190": "Queda não especificada",
    "W790": "Inalação e ingestão de alimentos causando obstrução das vias respiratórias",
    "X700": "Lesão autoprovocada intencionalmente (Suicídio)",
    "X740": "Lesão autoprovocada intencionalmente por disparo de arma de fogo",
    "X590": "Exposição a fatores não especificados como causa de ferimentos",
    "X990": "Agressão por objeto cortante"
}

def traduzir_cid(codigo):
    if pd.isna(codigo):
        return "Não Informado"
    codigo_limpo = str(codigo).strip().upper()
    return dicionario_cid.get(codigo_limpo, f"Outras Causas (CID: {codigo_limpo})")

if "CAUSABAS" in df.columns:
    df["CAUSA_DESC"] = df["CAUSABAS"].apply(traduzir_cid)
    df["LETRA_CID"] = df["CAUSABAS"].str.slice(0, 1).fillna("Outros")

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
if "LOCOCOR" in df.columns:
    df["LOCAL_DESC"] = df["LOCOCOR"].map(mapa_local).fillna("Não Informado")
else:
    df["LOCAL_DESC"] = "Não Informado"

# Tradução padronizada do Sexo no SIM
mapa_sexo = {1: "Masculino", 2: "Feminino"}
if "SEXO" in df.columns:
    df["SEXO_DESC"] = df["SEXO"].map(mapa_sexo).fillna("Não Informado")
else:
    df["SEXO_DESC"] = "Não Informado"

# Classificação de Causas Evitáveis / Atenção Primária
def eh_evitavel_aps(codigo):
    if pd.isna(codigo):
        return False
    c = str(codigo).strip().upper()
    prefixos_aps = ("I10", "I11", "I12", "I13", "E10", "E11", "E14", "J15", "J18", "N39", "A09")
    return c.startswith(prefixos_aps)

df["EVITAVEL_APS"] = df["CAUSABAS"].apply(eh_evitavel_aps)

# Barra Lateral - Filtros Globais
st.sidebar.header("🔍 Filtros Operacionais Globais")
anos_disponiveis = sorted(df["ANO_OBITO"].dropna().unique())
anos_selecionados = st.sidebar.multiselect("Selecione o(s) Ano(s):", options=anos_disponiveis, default=anos_disponiveis)

df_filtrado = df[df["ANO_OBITO"].isin(anos_selecionados)] if anos_selecionados else df.copy()

# Métricas Principais Ampliadas nos Cards de Topo
st.markdown("---")
total_obitos = len(df_filtrado)
total_homens = len(df_filtrado[df_filtrado["SEXO_DESC"] == "Masculino"])
total_mulheres = len(df_filtrado[df_filtrado["SEXO_DESC"] == "Feminino"])

media_h = int(df_filtrado[df_filtrado["SEXO_DESC"] == "Masculino"]["IDADE_ANOS"].mean()) if not df_filtrado[df_filtrado["SEXO_DESC"] == "Masculino"]["IDADE_ANOS"].dropna().empty else 0
media_m = int(df_filtrado[df_filtrado["SEXO_DESC"] == "Feminino"]["IDADE_ANOS"].mean()) if not df_filtrado[df_filtrado["SEXO_DESC"] == "Feminino"]["IDADE_ANOS"].dropna().empty else 0

total_evitaveis = df_filtrado["EVITAVEL_APS"].sum()

# Linha 1 de Cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de Óbitos", total_obitos)
c2.metric("👨 Óbitos Masculinos", total_homens)
c3.metric("👩 Óbitos Femininos", total_mulheres)
c4.metric("🛡️ Óbitos por Causas Evitáveis (APS)", total_evitaveis)

# Linha 2 de Cards
c5, c6, c7 = st.columns(3)
c5.metric("👨 Média de Idade (Homens)", f"{media_h} anos")
c6.metric("👩 Média de Idade (Mulheres)", f"{media_m} anos")
c7.metric("Município", "Porto Feliz - SP")
st.markdown("---")

# Abas para Organizar o Dashboard (Com a nova Aba 6)
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📈 Visão Geral", 
    "👥 Perfil & Local", 
    "🔬 Causas", 
    "📋 Tabela Interativa & Filtros", 
    "❤️ Análise por Gênero & Grupos CID-10",
    "🛡️ Óbitos Evitáveis (APS)"
])

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
        
    df_tabela = df_filtrado.copy()
    if faixa_filtro:
        df_tabela = df_tabela[df_tabela["FAIXA_ETARIA"].astype(str).isin(faixa_filtro)]
    if causa_filtro:
        df_tabela = df_tabela[df_tabela["CAUSA_DESC"].isin(causa_filtro)]
    if local_filtro:
        df_tabela = df_tabela[df_tabela["LOCAL_DESC"].isin(local_filtro)]
        
    st.markdown(f"**Registros encontrados com os filtros aplicados:** {len(df_tabela)}")
    
    colunas_exibicao = ["ANO_OBITO", "DTOBITO", "IDADE_ANOS", "FAIXA_ETARIA", "SEXO_DESC", "CAUSA_DESC", "LOCAL_DESC"]
    colunas_presentes = [c for c in colunas_exibicao if c in df_tabela.columns]
    
    st.dataframe(df_tabela[colunas_presentes], use_container_width=True)
    
    csv_dados = df_tabela[colunas_presentes].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados filtrados em CSV (para relatório)",
        data=csv_dados,
        file_name="obitos_porto_feliz_filtrado.csv",
        mime="text/csv",
    )

with aba5:
    st.subheader("❤️ Análise por Gênero, Faixa Etária e Grupos da CID-10")
    st.markdown("Selecione abaixo os agrupamentos de CID-10 que deseja incluir na análise comparativa entre homens e mulheres.")
    
    st.markdown("**Filtrar Grupos de Causas (CID-10):**")
    col_cb1, col_cb2, col_cb3, col_cb4, col_cb5 = st.columns(5)
    
    with col_cb1:
        chk_circulatorio = st.checkbox("❤️ Aparelho Circulatório (Letra I)", value=True)
    with col_cb2:
        chk_neoplasias = st.checkbox("🎗️ Neoplasias / Tumores (Letra C)", value=True)
    with col_cb3:
        chk_respiratorio = st.checkbox("🫁 Aparelho Respiratório (Letra J)", value=True)
    with col_cb4:
        chk_externas = st.checkbox("⚠️ Causas Externas / Acidentes (Letras V, W, X, Y)", value=True)
    with col_cb5:
        chk_outros = st.checkbox("📋 Outros Grupos / Demais Letras", value=True)
        
    letras_permitidas = []
    if chk_circulatorio:
        letras_permitidas.append("I")
    if chk_neoplasias:
        letras_permitidas.append("C")
    if chk_respiratorio:
        letras_permitidas.append("J")
    if chk_externas:
        letras_permitidas.extend(["V", "W", "X", "Y"])
    if chk_outros:
        todas_letras = df_filtrado["LETRA_CID"].unique()
        outras = [l for l in todas_letras if l not in ["I", "C", "J", "V", "W", "X", "Y"]]
        letras_permitidas.extend(outras)
        
    df_genero = df_filtrado[df_filtrado["LETRA_CID"].isin(letras_permitidas)]
    
    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("### 👨 Óbitos de Homens (Faixa Etária & Causa)")
        df_homens = df_genero[df_genero["SEXO_DESC"] == "Masculino"]
        if not df_homens.empty:
            cross_homens = df_homens.groupby(["FAIXA_ETARIA", "CAUSA_DESC"]).size().reset_index(name="Total")
            top_causas_h = df_homens["CAUSA_DESC"].value_counts().head(6).index.tolist()
            cross_homens_top = cross_homens[cross_homens["CAUSA_DESC"].isin(top_causas_h)]
            
            fig_h = px.bar(
                cross_homens_top, 
                x="FAIXA_ETARIA", 
                y="Total", 
                color="CAUSA_DESC", 
                barmode="stack",
                title="Homens: Causas por Faixa Etária"
            )
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")
            
    with col_g2:
        st.markdown("### 👩 Óbitos de Mulheres (Faixa Etária & Causa)")
        df_mulheres = df_genero[df_genero["SEXO_DESC"] == "Feminino"]
        if not df_mulheres.empty:
            cross_mulheres = df_mulheres.groupby(["FAIXA_ETARIA", "CAUSA_DESC"]).size().reset_index(name="Total")
            top_causas_m = df_mulheres["CAUSA_DESC"].value_counts().head(6).index.tolist()
            cross_mulheres_top = cross_mulheres[cross_mulheres["CAUSA_DESC"].isin(top_causas_m)]
            
            fig_m = px.bar(
                cross_mulheres_top, 
                x="FAIXA_ETARIA", 
                y="Total", 
                color="CAUSA_DESC", 
                barmode="stack",
                title="Mulheres: Causas por Faixa Etária"
            )
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")

with aba6:
    st.subheader("🛡️ Monitoramento de Óbitos por Causas Evitáveis (Atenção Primária à Saúde)")
    st.markdown("Esta aba isola os óbitos associados a agravos que poderiam ser prevenidos, controlados ou tratados de forma oportuna pelas equipes de saúde da família (hipertensão, diabetes, infecções tratáveis, etc.).")
    
    df_evitaveis = df_filtrado[df_filtrado["EVITAVEL_APS"] == True]
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.metric("Total de Óbitos Evitáveis no Período", len(df_evitaveis))
    with col_e2:
        perc = (len(df_evitaveis) / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
        st.metric("Percentual sobre o Total Geral", f"{perc:.1f}%")
        
    st.markdown("---")
    
    if not df_evitaveis.empty:
        col_graf, col_tab = st.columns([1, 1])
        
        with col_graf:
            st.subheader("📊 Principais Causas Evitáveis")
            top_evit = df_evitaveis["CAUSA_DESC"].value_counts().reset_index()
            top_evit.columns = ["Causa", "Total"]
            fig_evit = px.bar(top_evit, x="Total", y="Causa", orientation="h", color="Total", color_continuous_scale="Oranges", text="Total")
            fig_evit.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_evit, use_container_width=True)
            
        with col_tab:
            st.subheader("📋 Tabela Analítica de Óbitos Evitáveis")
            colunas_evit = ["ANO_OBITO", "DTOBITO", "IDADE_ANOS", "SEXO_DESC", "CAUSA_DESC", "LOCAL_DESC"]
            col_pres_evit = [c for c in colunas_evit if c in df_evitaveis.columns]
            st.dataframe(df_evitaveis[col_pres_evit], use_container_width=True)
            
            csv_evit = df_evitaveis[col_pres_evit].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar dados de Óbitos Evitáveis em CSV",
                data=csv_evit,
                file_name="obitos_evitaveis_porto_feliz.csv",
                mime="text/csv",
            )
    else:
        st.warning("Nenhum óbito evitável encontrado para os filtros selecionados.")
