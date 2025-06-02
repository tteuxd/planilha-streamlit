import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Planilha de Cadastro", layout="wide")

# Caminho do arquivo CSV
arquivo_csv = "dados.csv"

# Carregar Dados
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])

# Função para salvar os dados
def salvar_dados():
    df.to_csv(arquivo_csv, index=False)

# Função para colorir linhas
def highlight_row(row):
    status = str(row["Status"])
    if "Verificado" in status:
        return ["background-color: #d4edda; color: green"] * len(row)
    elif "Não Verificado" in status:
        return ["background-color: #f8d7da; color: red"] * len(row)
    elif "Comprando Artefato" in status or "Comprando Crystal" in status:
        return ["background-color: #fff3cd; color: orange"] * len(row)
    else:
        return [""] * len(row)

# Título
st.title("🗒️ Planilha de Cadastro de Jogadores")

# Mostrar dados
st.subheader("📑 Dados Cadastrados")

if not df.empty:
    styled_df = df.style.apply(highlight_row, axis=1)
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Nenhum dado cadastrado ainda.")

# Área de edição e cadastro
st.subheader("✍️ Adicionar, Editar ou Remover")

with st.expander("Gerenciar Dados"):
    col1, col2 = st.columns(2)

    if not df.empty:
        linha = st.selectbox(
            "Selecione uma linha para editar/remover (ou deixe vazio para adicionar novo):",
            options=[None] + list(df.index),
            format_func=lambda x: f"{df.loc[x, 'Nome']} - {df.loc[x, 'Classe']}" if x is not None else "Adicionar Novo"
        )
    else:
        linha = None

    if linha is not None:
        nome = col1.text_input("Nome", value=df.loc[linha, "Nome"])
        classe = col2.text_input("Classe", value=df.loc[linha, "Classe"])
        status_atual = df.loc[linha, "Status"].split(", ") if pd.notna(df.loc[linha, "Status"]) else []
    else:
        nome = col1.text_input("Nome")
        classe = col2.text_input("Classe")
        status_atual = []

    # Checkboxes para status
    verificado = st.checkbox("✅ Verificado", value="Verificado" in status_atual)
    nao_verificado = st.checkbox("❌ Não Verificado", value="Não Verificado" in status_atual)
    comprando_artefato = st.checkbox("🛒 Comprando Artefato", value="Comprando Artefato" in status_atual)
    comprando_crystal = st.checkbox("💎 Comprando Crystal", value="Comprando Crystal" in status_atual)

    # Montagem da string de status
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

    col3, col4, col5 = st.columns(3)

    # Botão Salvar
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
            st.experimental_rerun()
        else:
            st.warning("Preencha os campos de Nome e Classe.")

    # Botão Remover
    if col4.button("🗑️ Remover") and linha is not None:
        df = df.drop(linha).reset_index(drop=True)
        salvar_dados()
        st.success("Registro removido!")
        st.experimental_rerun()

    # Botão Limpar Campos
    if col5.button("♻️ Limpar Campos"):
        st.experimental_rerun()

# Exportação para Excel
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
