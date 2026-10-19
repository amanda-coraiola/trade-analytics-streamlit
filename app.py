import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Trade Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Estilização básica
st.title("📊 Painel de Trade Marketing & Performance de Vendas")
st.markdown("---")

# Carregamento de dados
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("sales_data.csv")
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    except FileNotFoundError:
        # Dados de exemplo caso o CSV ainda não tenha sido subido
        data = {
            "Data": pd.date_range(start="2026-01-01", periods=100, freq="D"),
            "Regiao": ["Sul", "Sudeste", "Nordeste", "Centro-Oeste"] * 25,
            "Canal": ["Varejo", "Atacado", "E-commerce"] * 33 + ["Varejo"],
            "Produto": ["Linha Premium", "Linha Standard", "Linha Eco"] * 33 + ["Linha Premium"],
            "Faturamento": [1200 + i * 15 for i in range(100)],
            "Volume_Unidades": [150 + i * 2 for i in range(100)],
            "Meta": [1300 + i * 12 for i in range(100)],
            "Ruptura_Pct": [2.5, 4.1, 1.8, 3.2] * 25
        }
        return pd.DataFrame(data)

df = load_data()

# Filtros na barra lateral
st.sidebar.header("🔍 Filtros de Análise")

regiao_sel = st.sidebar.multiselect(
    "Selecione a Região:",
    options=df["Regiao"].unique(),
    default=df["Regiao"].unique()
)

canal_sel = st.sidebar.multiselect(
    "Selecione o Canal de Vendas:",
    options=df["Canal"].unique(),
    default=df["Canal"].unique()
)

produto_sel = st.sidebar.multiselect(
    "Selecione o Produto:",
    options=df["Produto"].unique(),
    default=df["Produto"].unique()
)

# Filtragem do dataframe
df_filtered = df[
    (df["Regiao"].isin(regiao_sel)) &
    (df["Canal"].isin(canal_sel)) &
    (df["Produto"].isin(produto_sel))
]

# Indicadores Principais (KPIs)
col1, col2, col3, col4 = st.columns(4)

total_fatu = df_filtered["Faturamento"].sum()
total_meta = df_filtered["Meta"].sum()
atingimento = (total_fatu / total_meta * 100) if total_meta > 0 else 0
media_ruptura = df_filtered["Ruptura_Pct"].mean()

col1.metric("Faturamento Total", f"R$ {total_fatu:,.2f}")
col2.metric("Meta Prevista", f"R$ {total_meta:,.2f}")
col3.metric("Atingimento de Meta", f"{atingimento:.1f}%")
col4.metric("Taxa Média de Ruptura", f"{media_ruptura:.2f}%")

st.markdown("---")

# Gráficos de Performance
g1, g2 = st.columns(2)

with g1:
    st.subheader("📈 Faturamento por Canal de Vendas")
    fig_canal = px.bar(
        df_filtered.groupby("Canal")["Faturamento"].sum().reset_index(),
        x="Canal",
        y="Faturamento",
        color="Canal",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_canal, use_container_width=True)

with g2:
    st.subheader("🗺️ Faturamento por Região")
    fig_regiao = px.pie(
        df_filtered.groupby("Regiao")["Faturamento"].sum().reset_index(),
        names="Regiao",
        values="Faturamento",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_regiao, use_container_width=True)

# Evolução Temporal e Exportação
st.subheader("📅 Evolução do Faturamento ao Longo do Tempo")
fig_line = px.line(
    df_filtered.groupby("Data")[["Faturamento", "Meta"]].sum().reset_index(),
    x="Data",
    y=["Faturamento", "Meta"],
    markers=True
)
st.plotly_chart(fig_line, use_container_width=True)

# Tabela e Exportação
with st.expander("📄 Visualizar Tabela de Dados"):
    st.dataframe(df_filtered)
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv,
        file_name="dados_trade_filtrados.csv",
        mime="text/csv"
    )
