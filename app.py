import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Planilha de Cadastro", layout="wide")

# Inicializa session_state para evitar erros
for key, default in {
    "nome": "",
    "classe": "",
    "status_atual": [],
    "linha_selecionada": None,
    "confirmar_remocao": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Arquivo CSV para salvar dados
arquivo_csv = "dados.csv"

# Carregar dados
if os.path.exists(arquivo_csv):
    df = pd.read_csv(arquivo_csv)
else:
    df = pd.DataFrame(columns=["Nome", "Classe", "Status"])

# Função para salvar dados
def salvar_dados():
    df.to_csv(arquivo_csv, index=False)

# Função para colorir linhas conforme status
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

# Atualiza campos para edição ao selecionar linha
def selecionar_linha():
    idx = st.session_state.linha_selecionada
    if idx is not None:
        st.session_state.nome = df.loc[idx, "Nome"]
        st.session_state.classe = df.loc[idx, "Classe"]
        status = df.loc[idx, "Status"]
        st.session_state.status_atual = status.split(", ") if pd.notna(status) else []
    else:
        st.session_state.nome = ""
        st.session_state.classe = ""
        st.session_state.status_atual = []

st.title("🗒️ Planilha de Cadastro de Jogadores")

# Menu lateral - abas
aba = st.sidebar.selectbox("Escolha a aba", ["Cadastro", "Relatórios"])

if aba == "Cadastro":
    # Filtros de busca
    st.subheader("🔍 Filtro de Pesquisa")
    busca_nome = st.text_input("Buscar por Nome")
    busca_classe = st.text_input("Buscar por Classe")

    # Filtrar dataframe conforme busca
    df_filtrado = df.copy()
    if busca_nome:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(busca_nome, case=False, na=False)]
    if busca_classe:
        df_filtrado = df_filtrado[df_filtrado["Classe"].str.contains(busca_classe, case=False, na=False)]

    st.subheader("📑 Dados Cadastrados")
    if not df_filtrado.empty:
        styled_df = df_filtrado.style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado com esses filtros.")

    st.subheader("✍️ Adicionar, Editar ou Remover")

    with st.expander("Gerenciar Dados"):

        linha = st.selectbox(
            "Selecione para editar/remover (ou deixe vazio para adicionar):",
            options=[None] + list(df_filtrado.index),
            format_func=lambda x: f"{df.loc[x, 'Nome']} - {df.loc[x, 'Classe']}" if x is not None else "Adicionar Novo",
            key="linha_selecionada",
            on_change=selecionar_linha
        )

        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome", key="nome")
        classe = col2.text_input("Classe", key="classe")

        verificado = st.checkbox("✅ Verificado", value="Verificado" in st.session_state.status_atual)
        nao_verificado = st.checkbox("❌ Não Verificado", value="Não Verificado" in st.session_state.status_atual)
        comprando_artefato = st.checkbox("🛒 Comprando Artefato", value="Comprando Artefato" in st.session_state.status_atual)
        comprando_crystal = st.checkbox("💎 Comprando Crystal", value="Comprando Crystal" in st.session_state.status_atual)

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

        if col3.button("💾 Salvar"):
            if nome.strip() == "" or classe.strip() == "":
                st.warning("Preencha os campos de Nome e Classe.")
            else:
                if linha is not None:
                    df.loc[linha, "Nome"] = nome
                    df.loc[linha, "Classe"] = classe
                    df.loc[linha, "Status"] = status_text
                    st.success("Registro atualizado com sucesso!")
                else:
                    df.loc[len(df)] = {"Nome": nome, "Classe": classe, "Status": status_text}
                    st.success("Registro adicionado com sucesso!")
                salvar_dados()
                # Reset campos e seleção
                st.session_state.nome = ""
                st.session_state.classe = ""
                st.session_state.status_atual = []
                st.session_state.linha_selecionada = None
                st.session_state.confirmar_remocao = False
                st.experimental_rerun()

        # Botão remover com confirmação
        if col4.button("🗑️ Remover"):

            if linha is None:
                st.warning("Selecione um registro para remover.")
            else:
                st.session_state.confirmar_remocao = True

        if st.session_state.confirmar_remocao:
            st.warning(f"Tem certeza que deseja remover '{df.loc[st.session_state.linha_selecionada, 'Nome']}'?")
            col_confirma, col_cancela = st.columns(2)
            if col_confirma.button("Confirmar Remoção"):
                df.drop(st.session_state.linha_selecionada, inplace=True)
                df.reset_index(drop=True, inplace=True)
                salvar_dados()
                st.success("Registro removido!")
                # Reset campos e seleção
                st.session_state.nome = ""
                st.session_state.classe = ""
                st.session_state.status_atual = []
                st.session_state.linha_selecionada = None
                st.session_state.confirmar_remocao = False
                st.experimental_rerun()
            if col_cancela.button("Cancelar"):
                st.session_state.confirmar_remocao = False
                st.experimental_rerun()

        if col5.button("♻️ Limpar Campos"):
            st.session_state.nome = ""
            st.session_state.classe = ""
            st.session_state.status_atual = []
            st.session_state.linha_selecionada = None
            st.session_state.confirmar_remocao = False
            st.experimental_rerun()

elif aba == "Relatórios":
    st.header("📊 Relatórios de Status")

    cont_verificado = df["Status"].str.contains("Verificado", na=False).sum()
    cont_nao_verificado = df["Status"].str.contains("Não Verificado", na=False).sum()
    cont_comprando_artefato = df["Status"].str.contains("Comprando Artefato", na=False).sum()
    cont_comprando_crystal = df["Status"].str.contains("Comprando Crystal", na=False).sum()

    st.markdown("### Quantidade por Status")

    labels = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]
    sizes = [cont_verificado, cont_nao_verificado, cont_comprando_artefato, cont_comprando_crystal]
    colors = ['#d4edda', '#f8d7da', '#fff3cd', '#fff3cd']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax1.axis('equal')

    st.pyplot(fig1)

    st.markdown("### Gráfico de Barras")

    fig2, ax2 = plt.subplots()
    ax2.bar(labels, sizes, color=colors)
    ax2.set_ylabel('Quantidade')
    ax2.set_ylim(0, max(sizes) + 2)

    for i, v in enumerate(sizes):
        ax2.text(i, v + 0.1, str(v), ha='center', fontweight='bold')

    st.pyplot(fig2)

# Botão para exportar Excel (visível em todas abas)
if st.button("📤 Exportar para Excel"):
    df.to_excel("dados.xlsx", index=False)
    st.success("Arquivo 'dados.xlsx' exportado com sucesso!")
    with open("dados.xlsx", "rb") as f:
        st.download_button(
            label="📥 Baixar dados.xlsx",
            data=f,
            file_name="dados.xlsx",
        )
