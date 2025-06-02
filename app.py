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

st.sidebar.header("🔍 Filtros de Pesquisa")
filtro_nome = st.sidebar.text_input("Filtrar por nome")
filtro_classe = st.sidebar.selectbox("Filtrar por classe", [""] + CLASSES)
filtro_status = st.sidebar.multiselect("Filtrar por status", STATUS_OPCOES)

# Aplicando filtros
df_filtrado = df.copy()
if filtro_nome:
    df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(filtro_nome, case=False, na=False)]
if filtro_classe:
    df_filtrado = df_filtrado[df_filtrado["Classe"] == filtro_classe]
if filtro_status:
    df_filtrado = df_filtrado[df_filtrado["Status"].str.contains('|'.join(filtro_status))]

st.subheader("📑 Dados dos Membros")

# Colorir status
def colorir_linha(row):
    if "Não Verificado" in row["Status"]:
        return ['background-color: #ffcccc']*len(row)
    elif "Verificado" in row["Status"]:
        return ['background-color: #ccffcc']*len(row)
    elif "Comprando Artefato" in row["Status"] or "Comprando Crystal" in row["Status"]:
        return ['background-color: #fff2cc']*len(row)
    else:
        return ['']*len(row)

st.dataframe(
    df_filtrado.style.apply(colorir_linha, axis=1),
    use_container_width=True
)

st.divider()

# ==== Área de Cadastro e Edição ====
st.subheader("➕ Cadastro / ✏️ Edição")

with st.form("form_membro"):
    nome = st.text_input("Nome")
    classe = st.selectbox("Classe", CLASSES)
    status = st.multiselect("Status", STATUS_OPCOES)

    editar = st.checkbox("Editar membro existente")

    submit = st.form_submit_button("Salvar")

    if submit:
        if not nome or not status:
            st.warning("Preencha o nome e selecione pelo menos um status.")
        else:
            if editar:
                df.loc[df["Nome"] == nome, ["Classe", "Status"]] = [classe, ', '.join(status)]
                st.success(f"Membro {nome} atualizado!")
            else:
                novo = pd.DataFrame({"Nome": [nome], "Classe": [classe], "Status": [', '.join(status)]})
                df = pd.concat([df, novo], ignore_index=True)
                st.success(f"Membro {nome} adicionado!")

            df.to_excel(FILE_PATH, index=False)
            st.experimental_rerun()

# ==== Área de Seleção para Edição ====
st.subheader("✏️ Selecionar para Edição")

selecao = st.selectbox("Selecione um membro para preencher os campos", [""] + list(df_filtrado["Nome"]))

if selecao:
    membro = df[df["Nome"] == selecao].iloc[0]
    st.info(f"Preenchendo campos com dados de {selecao}")

    st.session_state["nome"] = membro["Nome"]
    st.session_state["classe"] = membro["Classe"]
    st.session_state["status"] = membro["Status"].split(", ")

# ==== Remover ====
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
