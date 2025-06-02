import streamlit as st
import pandas as pd
import os
from io import BytesIO
import matplotlib.pyplot as plt

# 🚀 Configuração da página
st.set_page_config(page_title="Planilha de Membros", page_icon="📑", layout="wide")

# 🎨 Lista de Classes (ordenada alfabeticamente)
classes_disponiveis = sorted([
    "Archer", "Berserker", "Corsair", "DarkKnight", "Deadeye", "Dosa", "Drakania", 
    "Guardian", "Hashashin", "Kunoichi", "Lahn", "Maegu", "Maehwa", "Musa", 
    "Mystic", "Ninja", "Nova", "Ranger", "Sage", "Scholar", "Shai", 
    "Sorceress", "Striker", "Tamer", "Valkyrie", "Warrior", "Witch", 
    "Wizard", "Woosa"
])

status_disponiveis = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]

# 📂 Carregamento ou criação do banco de dados
FILE_PATH = "dados.xlsx"
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])

# 🧠 Estado da sessão para controle
if "selecionado" not in st.session_state:
    st.session_state.selecionado = None

# 🔍 Filtros
with st.expander("🔍 Filtros de Pesquisa", expanded=True):
    col1, col2, col3 = st.columns(3)

    filtro_nome = col1.text_input("Buscar por Nome")
    filtro_classe = col2.selectbox("Filtrar por Classe", ["Todos"] + classes_disponiveis)
    filtro_status = col3.selectbox("Filtrar por Status", ["Todos"] + status_disponiveis)

    df_filtrado = df.copy()

    if filtro_nome:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(filtro_nome, case=False, na=False)]

    if filtro_classe != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Classe"] == filtro_classe]

    if filtro_status != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Status"].str.contains(filtro_status, na=False)]

st.subheader("📋 Cadastro de Membros")

# 🖊️ Formulário de cadastro/edição
with st.form(key="formulario"):
    col1, col2 = st.columns(2)

    nome = col1.text_input("Nome", value=st.session_state.selecionado["Nome"] if st.session_state.selecionado else "")
    classe = col2.selectbox("Classe", classes_disponiveis, 
                             index=classes_disponiveis.index(st.session_state.selecionado["Classe"]) 
                             if st.session_state.selecionado else 0)

    status = st.multiselect("Status", status_disponiveis, 
                             default=st.session_state.selecionado["Status"].split(", ") 
                             if st.session_state.selecionado else [])

    enviar = st.form_submit_button("Salvar")

    if enviar:
        if nome == "":
            st.warning("⚠️ O nome não pode estar vazio.")
        else:
            novo_dado = {"Nome": nome, "Classe": classe, "Status": ", ".join(status)}

            if st.session_state.selecionado:
                # Editar
                idx = df[(df["Nome"] == st.session_state.selecionado["Nome"]) & (df["Classe"] == st.session_state.selecionado["Classe"])].index
                df.loc[idx, ["Nome", "Classe", "Status"]] = [nome, classe, ", ".join(status)]
                st.success("✅ Registro editado com sucesso!")
            else:
                # Adicionar
                df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
                st.success("✅ Registro adicionado com sucesso!")

            df.to_excel(FILE_PATH, index=False)
            st.session_state.selecionado = None
            st.experimental_rerun()

st.subheader("📑 Lista de Membros")

# 🎨 Função para colorir linhas conforme status
def colorir_linha(status):
    if "Não Verificado" in status:
        return "background-color: #FFCCCC;"  # Vermelho claro
    elif "Verificado" in status:
        return "background-color: #CCFFCC;"  # Verde claro
    elif "Comprando Artefato" in status or "Comprando Crystal" in status:
        return "background-color: #FFE5B4;"  # Laranja claro
    return ""

# 🖥️ Mostrar tabela
styled_df = df_filtrado.style.apply(lambda x: [colorir_linha(x["Status"])] * len(x), axis=1)
st.dataframe(styled_df, use_container_width=True)

# 🔘 Ações
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ✏️ Editar")
    for i, row in df_filtrado.iterrows():
        if st.button(f"Editar {row['Nome']}"):
            st.session_state.selecionado = row
            st.experimental_rerun()

with col2:
    st.markdown("### 🗑️ Remover")
    for i, row in df_filtrado.iterrows():
        if st.button(f"Remover {row['Nome']}"):
            if st.confirm(f"Tem certeza que deseja remover {row['Nome']}?"):
                df = df.drop(index=i).reset_index(drop=True)
                df.to_excel(FILE_PATH, index=False)
                st.success(f"❌ {row['Nome']} removido!")
                st.experimental_rerun()

with col3:
    st.markdown("### 📥 Exportar")
    def gerar_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Membros')
        output.seek(0)
        return output

    excel_bytes = gerar_excel(df_filtrado)

    st.download_button(
        label="📥 Baixar Excel",
        data=excel_bytes,
        file_name="dados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 📊 Relatórios
st.subheader("📊 Relatórios e Gráficos")

aba1, aba2 = st.tabs(["Por Status", "Por Classe"])

with aba1:
    status_contagem = df["Status"].str.get_dummies(sep=', ').sum()

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

