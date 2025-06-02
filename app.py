import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Planilha de Cadastro", layout="wide")

# Arquivo CSV
arquivo_csv = "dados.csv"

# Carregar dados
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])

# Salvar dados
def salvar_dados():
    df.to_csv(arquivo_csv, index=False)

# Função para colorir linhas
def highlight_row(row):
    status = str(row["Status"])
    if "Não Verificado" in status:
        return ["background-color: #f8d7da; color: red"] * len(row)
    elif "Verificado" in status:
        return ["background-color: #d4edda; color: green"] * len(row)
    elif "Comprando Artefato" in status or "Comprando Crystal" in status:
        return ["background-color: #fff3cd; color: orange"] * len(row)
    else:
        return [""] * len(row)

# 🔥 Callback que preenche os campos quando muda o selectbox
def selecionar_linha():
    if st.session_state.linha_selecionada is not None:
        st.session_state.nome = df.loc[st.session_state.linha_selecionada, "Nome"]
        st.session_state.classe = df.loc[st.session_state.linha_selecionada, "Classe"]
        status = df.loc[st.session_state.linha_selecionada, "Status"]
        st.session_state.status_atual = status.split(", ") if pd.notna(status) else []
    else:
        st.session_state.nome = ""
        st.session_state.classe = ""
        st.session_state.status_atual = []

# Título
st.title("🗒️ Planilha de Cadastro de Jogadores")

# Mostrar dados
st.subheader("📑 Dados Cadastrados")

if not df.empty:
    styled_df = df.style.apply(highlight_row, axis=1)
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Nenhum dado cadastrado ainda.")

# Gerenciar dados
st.subheader("✍️ Adicionar, Editar ou Remover")

with st.expander("Gerenciar Dados"):

    # Selectbox para selecionar a linha
    linha = st.selectbox(
        "Selecione para editar/remover (ou deixe vazio para adicionar):",
        options=[None] + list(df.index),
        format_func=lambda x: f"{df.loc[x, 'Nome']} - {df.loc[x, 'Classe']}" if x is not None else "Adicionar Novo",
        key="linha_selecionada",
        on_change=selecionar_linha
    )

    # Campos de texto
    col1, col2 = st.columns(2)
    nome = col1.text_input("Nome", key="nome")
    classe = col2.text_input("Classe", key="classe")

    # Checkboxes
    verificado = st.checkbox("✅ Verificado", value="Verificado" in st.session_state.get("status_atual", []))
    nao_verificado = st.checkbox("❌ Não Verificado", value="Não Verificado" in st.session_state.get("status_atual", []))
    comprando_artefato = st.checkbox("🛒 Comprando Artefato", value="Comprando Artefato" in st.session_state.get("status_atual", []))
    comprando_crystal = st.checkbox("💎 Comprando Crystal", value="Comprando Crystal" in st.session_state.get("status_atual", []))

    # Montar status
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

    # Botões
    col3, col4, col5 = st.columns(3)

    if col3.button("💾 Salvar"):
        if nome and classe:
            if linha is not None:
                df.loc[linha, "Nome"] = nome
                df.loc[linha, "Classe"] = classe
                df.loc[linha, "Status"] = status_text
                st.success("Registro atualizado com sucesso!")
            else:
                novo = {"Nome": nome, "Classe": classe, "Status": status_text}
                df.loc[len(df)] = novo
                st.success("Registro adicionado com sucesso!")
            salvar_dados()
            st.session_state.nome = ""
            st.session_state.classe = ""
            st.session_state.status_atual = []
            st.session_state.linha_selecionada = None
            st.experimental_rerun()
        else:
            st.warning("Preencha os campos de Nome e Classe.")

    if col4.button("🗑️ Remover") and linha is not None:
        df = df.drop(linha).reset_index(drop=True)
        salvar_dados()
        st.success("Registro removido!")
        st.session_state.nome = ""
        st.session_state.classe = ""
        st.session_state.status_atual = []
        st.session_state.linha_selecionada = None
        st.experimental_rerun()

    if col5.button("♻️ Limpar Campos"):
        st.session_state.nome = ""
        st.session_state.classe = ""
        st.session_state.status_atual = []
        st.session_state.linha_selecionada = None
        st.experimental_rerun()

# Exportação
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
