import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Planilha de Membros", layout="wide")

FILE_PATH = "dados_membros.xlsx"

CLASSES = sorted([
    "Archer", "Berserker", "Corsair", "DarkKnight", "Deadeye", "Dosa",
    "Drakania", "Guardian", "Hashashin", "Kunoichi", "Lahn", "Maegu",
    "Maehwa", "Musa", "Mystic", "Ninja", "Nova", "Ranger", "Sage",
    "Scholar", "Shai", "Sorceress", "Striker", "Tamer", "Valkyrie",
    "Warrior", "Witch", "Wizard", "Woosa"
])

STATUS_OPCOES = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]

# ==== Carregar dados na sessão ====
if "df_membros" not in st.session_state:
    if os.path.exists(FILE_PATH):
        st.session_state.df_membros = pd.read_excel(FILE_PATH)
    else:
        st.session_state.df_membros = pd.DataFrame(columns=["Nome", "Classe", "Status"])

# ==== Normalizar nome ====
st.session_state.df_membros["Nome"] = st.session_state.df_membros["Nome"].astype(str).str.strip().str.title()

# ==== Sidebar ====
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Escolha a Página", ["Gerenciamento de Membros", "Relatórios"])

# ==== Página: Gerenciamento de Membros ====
if pagina == "Gerenciamento de Membros":
    st.title("📋 Gerenciamento de Membros")

    df = st.session_state.df_membros

    st.subheader("🔍 Filtros de Pesquisa")
    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        filtro_nome = st.text_input("Filtrar por nome")
    with colf2:
        filtro_classe = st.selectbox("Filtrar por classe", [""] + CLASSES)
    with colf3:
        filtro_status = st.multiselect("Filtrar por status", STATUS_OPCOES)

    df_filtrado = df.copy()

    if filtro_nome:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(filtro_nome, case=False, na=False)]
    if filtro_classe:
        df_filtrado = df_filtrado[df_filtrado["Classe"] == filtro_classe]
    if filtro_status:
        df_filtrado = df_filtrado[
            df_filtrado["Status"].apply(
                lambda x: any(fs in str(x).split(", ") for fs in filtro_status)
            )
        ]

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
        nomes_para_editar = ["Novo Jogador"] + df_filtrado["Nome"].tolist()
    else:
        nomes_para_editar = ["Novo Jogador"]

    linha_selecionada = st.selectbox("Clique em um membro para editar", nomes_para_editar)

    if linha_selecionada == "Novo Jogador":
        nome = ""
        classe = CLASSES[0]
        status = []
    else:
        dados = df[df["Nome"] == linha_selecionada].iloc[0]
        nome = dados["Nome"]
        classe = dados["Classe"]
        status = dados["Status"].split(", ") if isinstance(dados["Status"], str) else []

    st.subheader("➕ Cadastro / Edição de Membros")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome", value=nome).strip().title()
        classe = st.selectbox("Classe", CLASSES, index=CLASSES.index(classe) if classe in CLASSES else 0)

    with col2:
        status = st.multiselect("Status", STATUS_OPCOES, default=status)

    col3, col4 = st.columns(2)

    with col3:
        if st.button("💾 Salvar"):
            if nome:
                status_str = ", ".join(status)

                if nome in df["Nome"].values:
                    st.session_state.df_membros.loc[st.session_state.df_membros["Nome"] == nome, ["Classe", "Status"]] = [classe, status_str]
                    st.success(f"Membro {nome} atualizado.")
                else:
                    st.session_state.df_membros.loc[len(st.session_state.df_membros)] = [nome, classe, status_str]
                    st.success(f"Membro {nome} adicionado.")

                st.session_state.df_membros.to_excel(FILE_PATH, index=False)
            else:
                st.warning("⚠️ Preencha o campo Nome.")

    with col4:
        if linha_selecionada != "Novo Jogador":
            if st.button("🗑️ Excluir Membro"):
                st.session_state.df_membros = st.session_state.df_membros[st.session_state.df_membros["Nome"] != linha_selecionada]
                st.session_state.df_membros.to_excel(FILE_PATH, index=False)
                st.success(f"Membro {linha_selecionada} excluído.")

    st.subheader("📤 Exportar Dados")
    buffer = BytesIO()
    st.session_state.df_membros.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Baixar Excel",
        data=buffer.getvalue(),
        file_name="dados_membros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ==== Página: Relatórios ====
if pagina == "Relatórios":
    st.title("📊 Relatórios de Membros")

    df = st.session_state.df_membros

    aba1, aba2 = st.tabs(["Status dos Membros", "Distribuição de Classes"])

    with aba1:
        st.subheader("📈 Status dos Membros")
        if df.empty:
            st.info("Sem dados para gerar o gráfico.")
        else:
            status_counts = df["Status"].str.get_dummies(sep=", ").sum()
            if not status_counts.empty:
                colors = plt.cm.Set3.colors
                fig1, ax1 = plt.subplots()
                ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
                ax1.set_title("Distribuição por Status")
                ax1.axis('equal')
                st.pyplot(fig1)
            else:
                st.info("Sem dados para gerar o gráfico.")

    with aba2:
        st.subheader("📊 Distribuição de Classes")
        if df.empty:
            st.info("Sem dados para gerar o gráfico.")
        else:
            classe_counts = df["Classe"].value_counts()
            if not classe_counts.empty:
                fig2, ax2 = plt.subplots()
                ax2.bar(classe_counts.index, classe_counts.values, color="skyblue")
                plt.xticks(rotation=90)
                ax2.set_ylabel("Quantidade")
                ax2.set_title("Distribuição de Classes")
                st.pyplot(fig2)
            else:
                st.info("Sem dados para gerar o gráfico.")
