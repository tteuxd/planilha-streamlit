import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Planilha de Membros", layout="wide")

FILE_PATH = "dados_membros.xlsx"

CLASSES = sorted([
    "Warrior", "Ranger", "Berserker", "Sorceress", "Valkyrie", "Wizard", "Witch", "Tamer",
    "Musa", "Maehwa", "Ninja", "Kunoichi", "DarkKnight", "Striker", "Mystic", "Lahn",
    "Archer", "Shai", "Guardian", "Hashashin", "Nova", "Sage", "Corsair", "Drakania",
    "Maegu", "Woosa", "Scholar", "Dosa", "Deadeye"
])

STATUS_OPCOES = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]

# Carregar dados
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])

st.title("📋 Planilha de Controle de Membros")

# ==== Filtros ====
st.sidebar.header("🔍 Filtros de Pesquisa")
filtro_nome = st.sidebar.text_input("Filtrar por nome")
filtro_classe = st.sidebar.selectbox("Filtrar por classe", [""] + CLASSES)
filtro_status = st.sidebar.multiselect("Filtrar por status", STATUS_OPCOES)

df_filtrado = df.copy()
if filtro_nome:
    df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(filtro_nome, case=False, na=False)]
if filtro_classe:
    df_filtrado = df_filtrado[df_filtrado["Classe"] == filtro_classe]
if filtro_status:
    df_filtrado = df_filtrado[df_filtrado["Status"].str.contains('|'.join(filtro_status))]

# ==== Formulário ====
st.subheader("➕ Cadastro / Edição de Membros")

col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome")
    classe = st.selectbox("Classe", CLASSES)

with col2:
    status = st.multiselect("Status", STATUS_OPCOES)

# ==== Tabela com clique para editar ====
st.subheader("📑 Dados dos Membros")

def cor_status(val):
    if pd.isna(val):
        return "color: black"
    elif "Não Verificado" in val:
        return "color: red"
    elif "Verificado" in val:
        return "color: green"
    elif "Comprando Artefato" in val or "Comprando Crystal" in val:
        return "color: orange"
    else:
        return "color: black"

if not df_filtrado.empty:
    st.dataframe(
        df_filtrado.style.applymap(cor_status, subset=["Status"]),
        use_container_width=True,
        height=400
    )

    linha_selecionada = st.selectbox("Clique para editar", df_filtrado["Nome"])

    if linha_selecionada:
        dados = df_filtrado[df_filtrado["Nome"] == linha_selecionada].iloc[0]
        nome = dados["Nome"]
        classe = dados["Classe"]
        status = dados["Status"].split(", ") if isinstance(dados["Status"], str) else []

# ==== Salvar / Adicionar ====
if st.button("💾 Salvar"):
    if nome:
        status_str = ", ".join(status)

        if nome in df["Nome"].values:
            df.loc[df["Nome"] == nome, ["Classe", "Status"]] = [classe, status_str]
            st.success(f"Membro {nome} atualizado.")
        else:
            df.loc[len(df)] = [nome, classe, status_str]
            st.success(f"Membro {nome} adicionado.")

        df.to_excel(FILE_PATH, index=False)
    else:
        st.warning("⚠️ Preencha o campo Nome.")

# ==== Relatórios ====
st.subheader("📊 Relatórios")

aba1, aba2 = st.tabs(["Status dos Membros", "Distribuição de Classes"])

with aba1:
    status_counts = df["Status"].str.get_dummies(sep=", ").sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

with aba2:
    classe_counts = df["Classe"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.bar(classe_counts.index, classe_counts.values, color="skyblue")
    plt.xticks(rotation=90)
    ax2.set_ylabel("Quantidade")
    ax2.set_title("Distribuição de Classes")
    st.pyplot(fig2)

# ==== Exportação ====
st.subheader("📤 Exportar Dados")
buffer = BytesIO()
df.to_excel(buffer, index=False)
st.download_button(
    label="📥 Baixar Excel",
    data=buffer.getvalue(),
    file_name="dados_membros.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
