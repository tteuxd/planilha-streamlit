import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Planilha de Cadastro", layout="wide")

# ----- Carregar Dados -----
arquivo_csv = "dados.csv"

if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])


# ----- Funções -----
def salvar_dados():
    df.to_csv(arquivo_csv, index=False)


def definir_cor(status):
    if "Verificado" in status:
        return "green"
    elif "Não Verificado" in status:
        return "red"
    elif "Comprando Artefato" in status or "Comprando Crystal" in status:
        return "orange"
    else:
        return "black"


# ----- Interface -----
st.title("🔖 Planilha de Cadastro")

st.sidebar.header("Adicionar ou Editar")

nome = st.sidebar.text_input("Nome")
classe = st.sidebar.text_input("Classe")

verificado = st.sidebar.checkbox("Verificado")
nao_verificado = st.sidebar.checkbox("Não Verificado")
comprando_artefato = st.sidebar.checkbox("Comprando Artefato")
comprando_crystal = st.sidebar.checkbox("Comprando Crystal")

status_list = []
if verificado:
    status_list.append("Verificado")
if nao_verificado:
    status_list.append("Não Verificado")
if comprando_artefato:
    status_list.append("Comprando Artefato")
if comprando_crystal:
    status_list.append("Comprando Crystal")

status_text = ", ".join(status_list)


# ----- Adicionar -----
if st.sidebar.button("Adicionar"):
    if nome and classe:
        novo_dado = {"Nome": nome, "Classe": classe, "Status": status_text}
        df.loc[len(df)] = novo_dado
        salvar_dados()
        st.sidebar.success("Adicionado com sucesso!")
        st.experimental_rerun()
    else:
        st.sidebar.warning("Preencha Nome e Classe")


# ----- Mostrar Dados -----
st.subheader("📑 Dados Cadastrados")

if not df.empty:
    # Adicionar cores
    styled_df = df.style.apply(
        lambda x: [
            f"color: {definir_cor(str(v))}"
            for v in x["Status"]
        ],
        axis=1
    )

    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Nenhum dado cadastrado ainda.")


# ----- Selecionar Linha para Editar -----
st.subheader("✍️ Editar ou Remover Registro")

if not df.empty:
    linha = st.selectbox(
        "Selecione a linha para editar/remover:",
        df.index,
        format_func=lambda x: f"{df.loc[x, 'Nome']} - {df.loc[x, 'Classe']}"
    )

    nome_edit = st.text_input("Editar Nome", df.loc[linha, "Nome"])
    classe_edit = st.text_input("Editar Classe", df.loc[linha, "Classe"])

    status_atual = df.loc[linha, "Status"].split(", ")

    verificado_edit = st.checkbox("Verificado", value="Verificado" in status_atual, key="verificado_edit")
    nao_verificado_edit = st.checkbox("Não Verificado", value="Não Verificado" in status_atual, key="nao_verificado_edit")
    artefato_edit = st.checkbox("Comprando Artefato", value="Comprando Artefato" in status_atual, key="artefato_edit")
    crystal_edit = st.checkbox("Comprando Crystal", value="Comprando Crystal" in status_atual, key="crystal_edit")

    status_edit = []
    if verificado_edit:
        status_edit.append("Verificado")
    if nao_verificado_edit:
        status_edit.append("Não Verificado")
    if artefato_edit:
        status_edit.append("Comprando Artefato")
    if crystal_edit:
        status_edit.append("Comprando Crystal")

    status_edit_text = ", ".join(status_edit)

    col1, col2 = st.columns(2)

    if col1.button("Salvar Alterações"):
        df.loc[linha, "Nome"] = nome_edit
        df.loc[linha, "Classe"] = classe_edit
        df.loc[linha, "Status"] = status_edit_text
        salvar_dados()
        st.success("Alterações salvas!")
        st.experimental_rerun()

    if col2.button("Remover"):
        df = df.drop(linha).reset_index(drop=True)
        salvar_dados()
        st.success("Registro removido!")
        st.experimental_rerun()


# ----- Exportar -----
st.subheader("📤 Exportar Dados")

if st.button("Exportar para Excel"):
    df.to_excel("dados.xlsx", index=False)
    st.success("Arquivo 'dados.xlsx' exportado com sucesso!")
    with open("dados.xlsx", "rb") as f:
        st.download_button(
            label="📥 Baixar dados.xlsx",
            data=f,
            file_name="dados.xlsx"
        )
