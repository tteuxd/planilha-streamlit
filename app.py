import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Planilha de Membros", layout="wide")

FILE_PATH = "dados_membros.xlsx"

# Lista de classes em ordem alfabética
CLASSES = [
    "Archer", "Berserker", "Corsair", "DarkKnight", "Deadeye",
    "Dosa", "Drakania", "Guardian", "Hashashin", "Kunoichi",
    "Lahn", "Maegu", "Maehwa", "Musa", "Mystic", "Ninja",
    "Nova", "Ranger", "Sage", "Scholar", "Shai", "Sorceress",
    "Striker", "Tamer", "Valkyrie", "Warrior", "Witch", "Wizard", "Woosa"
]

STATUS_OPCOES = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]

# Carregar dados ou criar arquivo
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

# ==== Área de Cadastro e Edição ====
st.subheader("➕ Cadastro / ✏️ Edição")

# ==== Detectar clique na tabela ====
linha_selecionada = st.radio(
    "Clique no nome para editar:",
    options=[""] + list(df_filtrado["Nome"]),
    horizontal=True
)

if linha_selecionada:
    membro = df[df["Nome"] == linha_selecionada].iloc[0]
    nome = membro["Nome"]
    classe = membro["Classe"]
    status = membro["Status"].split(", ")
    editar = True
else:
    nome = ""
    classe = CLASSES[0]
    status = []
    editar = False

with st.form("form_membro"):
    nome_input = st.text_input("Nome", value=nome)
    classe_input = st.selectbox("Classe", CLASSES, index=CLASSES.index(classe) if classe in CLASSES else 0)
    status_input = st.multiselect("Status", STATUS_OPCOES, default=status)

    submit = st.form_submit_button("Salvar")

    if submit:
        if not nome_input or not status_input:
            st.warning("Preencha o nome e selecione pelo menos um status.")
        else:
            if editar:
                df.loc[df["Nome"] == nome, ["Nome", "Classe", "Status"]] = [
                    nome_input, classe_input, ', '.join(status_input)
                ]
                st.success(f"Membro {nome_input} atualizado!")
            else:
                novo = pd.DataFrame({"Nome": [nome_input], "Classe": [classe_input], "Status": [', '.join(status_input)]})
                df = pd.concat([df, novo], ignore_index=True)
                st.success(f"Membro {nome_input} adicionado!")

            df.to_excel(FILE_PATH, index=False)
            st.experimental_rerun()

# ==== Mostrar Tabela ====
st.subheader("📑 Dados dos Membros")

def colorir_linha(row):
    styles = ['color: black'] * len(row)  # 🔥 Texto preto
    if "Não Verificado" in row["Status"]:
        styles = ['background-color: #ffcccc; color: black'] * len(row)
    elif "Verificado" in row["Status"]:
        styles = ['background-color: #ccffcc; color: black'] * len(row)
    elif "Comprando Artefato" in row["Status"] or "Comprando Crystal" in row["Status"]:
        styles = ['background-color: #fff2cc; color: black'] * len(row)
    return styles

st.dataframe(
    df_filtrado.style.apply(colorir_linha, axis=1),
    use_container_width=True
)

st.divider()

# ==== Remoção ====
st.subheader("🗑️ Remover Membros")

for i, row in df_filtrado.iterrows():
    with st.expander(f"Remover {row['Nome']}"):
        confirmar = st.checkbox(f"Confirmar remoção de {row['Nome']}", key=f"confirm_{i}")
        if confirmar:
            if st.button(f"Remover {row['Nome']}", key=f"remover_{i}"):
                df = df.drop(index=i).reset_index(drop=True)
                df.to_excel(FILE_PATH, index=False)
                st.success(f"❌ {row['Nome']} removido!")
                st.experimental_rerun()

st.divider()

# ==== Relatórios ====
st.subheader("📊 Relatórios e Gráficos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 Distribuição de Status")
    status_counts = df["Status"].str.get_dummies(sep=", ").sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

with col2:
    st.markdown("#### 📈 Distribuição de Classes")
    class_counts = df["Classe"].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.bar(class_counts.index, class_counts.values, color='skyblue')
    plt.xticks(rotation=90)
    st.pyplot(fig2)

st.divider()

# ==== Exportar ====
st.subheader("⬇️ Exportar Dados")
st.download_button(
    label="📥 Baixar Excel",
    data=df_filtrado.to_excel(index=False, engine='openpyxl'),
    file_name="membros.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
