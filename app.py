import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Gestão de Membros", layout="wide")

# 📦 Arquivo para salvar os dados
ARQUIVO_DADOS = "dados.csv"

# 🏹 Lista de Classes (em ordem alfabética)
CLASSES = [
    "Archer", "Berserker", "Corsair", "DarkKnight", "Deadeye", "Dosa", "Drakania",
    "Guardian", "Hashashin", "Kunoichi", "Lahn", "Maegu", "Maehwa", "Mistic", "Musa",
    "Ninja", "Nova", "Ranger", "Sage", "Scholar", "Shai", "Sorceress", "Striker",
    "Tamer", "Valkyrie", "Warrior", "Witch", "Wizard", "Woosa"
]

# ✔️ Lista de Status possíveis
STATUS_LIST = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]

# 🚀 Função para carregar dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS).fillna("")
    else:
        return pd.DataFrame(columns=["Nome", "Classe", "Status"])

# 💾 Função para salvar dados
def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

# 🎨 Função para colorir status
def cor_status(val):
    if "Não Verificado" in val:
        return 'color: red'
    elif "Verificado" in val:
        return 'color: green'
    elif "Comprando Artefato" in val or "Comprando Crystal" in val:
        return 'color: orange'
    else:
        return ''

# 🔎 Sidebar de filtros
st.sidebar.title("🔍 Filtros")
filtro_nome = st.sidebar.text_input("Pesquisar por Nome")
filtro_classe = st.sidebar.selectbox("Filtrar por Classe", ["Todos"] + CLASSES)
filtro_status = st.sidebar.multiselect("Filtrar por Status", STATUS_LIST)

# 🎯 Dados
df = carregar_dados()

# 🔨 Seção de cadastro/edição
st.title("📋 Gestão de Membros")

with st.expander("➕ Adicionar / Editar Membro"):
    nome = st.text_input("Nome")
    classe = st.selectbox("Classe", CLASSES)
    status = st.multiselect("Status", STATUS_LIST)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar"):
            if nome:
                novo = pd.DataFrame([[nome, classe, ",".join(status)]], columns=["Nome", "Classe", "Status"])
                # Verifica se já existe o nome, então edita
                df = df[df["Nome"] != nome]
                df = pd.concat([df, novo], ignore_index=True)
                salvar_dados(df)
                st.success(f"✅ Dados salvos para {nome}")
                st.experimental_rerun()
            else:
                st.warning("⚠️ Nome não pode estar vazio.")

    with col2:
        if st.button("Limpar"):
            st.experimental_rerun()

# 🗑️ Remoção com confirmação
st.subheader("🗑️ Remover Membro")
nome_para_remover = st.selectbox("Selecione um membro para remover", [""] + df["Nome"].tolist())
if nome_para_remover:
    if st.button("Remover"):
        if st.confirm(f"Tem certeza que deseja remover {nome_para_remover}?"):
            df = df[df["Nome"] != nome_para_remover]
            salvar_dados(df)
            st.success(f"✅ {nome_para_remover} removido com sucesso.")
            st.experimental_rerun()

# 🔥 Aplicação de Filtros
df_filtrado = df.copy()

if filtro_nome:
    df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(filtro_nome, case=False, na=False)]

if filtro_classe != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Classe"] == filtro_classe]

if filtro_status:
    df_filtrado = df_filtrado[df_filtrado["Status"].apply(lambda x: any(s in x for s in filtro_status))]

# 🖼️ Exibição dos dados
st.subheader("📑 Lista de Membros")
st.dataframe(df_filtrado.style.applymap(cor_status, subset=["Status"]), use_container_width=True)

# 📤 Exportar dados
st.download_button(
    "📥 Baixar como Excel",
    data=df_filtrado.to_excel(index=False, engine='openpyxl'),
    file_name="dados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 📊 Relatórios e Gráficos
st.subheader("📊 Relatórios")

aba1, aba2 = st.tabs(["Gráfico de Status", "Gráfico de Classes"])

with aba1:
    status_contagem = df["Status"].str.get_dummies(sep=",").sum()

    fig1, ax1 = plt.subplots()
    ax1.pie(status_contagem, labels=status_contagem.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    st.bar_chart(status_contagem)

with aba2:
    classe_contagem = df["Classe"].value_counts()

    fig2, ax2 = plt.subplots()
    ax2.pie(classe_contagem, labels=classe_contagem.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)

    st.bar_chart(classe_contagem)
