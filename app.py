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

# ==== Carregar dados ====
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])

# ==== Sidebar ====
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Escolha a Página", ["Gerenciamento de Membros", "Relatórios"])

# ==== Página: Gerenciamento de Membros ====
if pagina == "Gerenciamento de Membros":
    st.title("📋 Gerenciamento de Membros")

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
        df_filtrado = df_filtrado[df_filtrado["Status"].str.contains('|'.join(filtro_status))]

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

        linha_selecionada = st.selectbox("Clique em um membro para editar", df_filtrado["Nome"])

        if linha_selecionada:
            dados = df_filtrado[df_filtrado["Nome"] == linha_selecionada].iloc[0]
            nome = dados["Nome"]
            classe = dados["Classe"]
            status = dados["Status"].split(", ") if isinstance(dados["Status"], str) else []
    else:
        nome = ""
        classe = CLASSES[0]
        status = []

    st.subheader("➕ Cadastro / Edição de Membros")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome", value=nome)
        classe = st.selectbox("Classe", CLASSES, index=CLASSES.index(classe) if classe in CLASSES else 0)

    with col2:
        status = st.multiselect("Status", STATUS_OPCOES, default=status)

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

    st.subheader("📤 Exportar Dados")
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Baixar Excel",
        data=buffer.getvalue(),
        file_name="dados_membros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ==== Página: Relatórios ====
if pagina == "Relatórios":
    st.title("📊 Relatórios de Membros")

    aba1, aba2 = st.tabs(["Status dos Membros", "Distribuição de Classes"])

    with aba1:
        st.subheader("📈 Status dos Membros")
        status_counts = df["Status"].str.get_dummies(sep=", ").sum()
        if not status_counts.empty:
            fig1, ax1 = plt.subplots()
            ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        else:
            st.info("Sem dados para gerar o gráfico.")

    with aba2:
        st.subheader("📊 Distribuição de Classes")
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
