import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

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

# Callback para preencher os campos ao mudar a seleção
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

st.title("🗒️ Planilha de Cadastro de Jogadores")

# === Menu lateral para escolher a aba ===
aba = st.sidebar.selectbox("Escolha a aba", ["Cadastro", "Relatórios"])

if aba == "Cadastro":
    # === FILTRO DE PESQUISA ===
    st.subheader("🔍 Filtro de Pesquisa")
    busca_nome = st.text_input("Buscar por Nome")
    busca_classe = st.text_input("Buscar por Classe")

    # Filtrar dataframe
    df_filtrado = df.copy()
    if busca_nome:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(busca_nome, case=False, na=False)]
    if busca_classe:
        df_filtrado = df_filtrado[df_filtrado["Classe"].str.contains(busca_classe, case=False, na=False)]

    # Mostrar tabela filtrada
    st.subheader("📑 Dados Cadastrados")
    if not df_filtrado.empty:
        styled_df = df_filtrado.style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado com esses filtros.")

    # === Gerenciar dados ===
    st.subheader("✍️ Adicionar, Editar ou Remover")

    with st.expander("Gerenciar Dados"):

        # Selectbox para editar
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

        # Checkboxes de status
        verificado = st.checkbox("✅ Verificado", value="Verificado" in st.session_state.get("status_atual", []))
        nao_verificado = st.checkbox("❌ Não Verificado", value="Não Verificado" in st.session_state.get("status_atual", []))
        comprando_artefato = st.checkbox("🛒 Comprando Artefato", value="Comprando Artefato" in st.session_state.get("status_atual", []))
        comprando_crystal = st.checkbox("💎 Comprando Crystal", value="Comprando Crystal" in st.session_state.get("status_atual", []))

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

        # Confirmação antes de remover usando modal customizado
        if col4.button("🗑️ Remover") and linha is not None:
            with st.modal("Confirmação de Remoção", True):
                st.write(f"Tem certeza que deseja remover '{df.loc[linha, 'Nome']}'?")
                if st.button("Confirmar Remoção"):
                    df.drop(linha, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    salvar_dados()
                    st.success("Registro removido!")
                    st.session_state.nome = ""
                    st.session_state.classe = ""
                    st.session_state.status_atual = []
                    st.session_state.linha_selecionada = None
                    st.experimental_rerun()
                if st.button("Cancelar"):
                    st.experimental_rerun()

        if col5.button("♻️ Limpar Campos"):
            st.session_state.nome = ""
            st.session_state.classe = ""
            st.session_state.status_atual = []
            st.session_state.linha_selecionada = None
            st.experimental_rerun()

elif aba == "Relatórios":
    st.header("📊 Relatórios de Status")

    # Contar status
    cont_verificado = df["Status"].str.contains("Verificado", na=False).sum()
    cont_nao_verificado = df["Status"].str.contains("Não Verificado", na=False).sum()
    cont_comprando_artefato = df["Status"].str.contains("Comprando Artefato", na=False).sum()
    cont_comprando_crystal = df["Status"].str.contains("Comprando Crystal", na=False).sum()

    st.markdown("### Quantidade por Status")

    # Gráfico Pizza
    labels = ["Verificado", "Não Verificado", "Comprando Artefato", "Comprando Crystal"]
    sizes = [cont_verificado, cont_nao_verificado, cont_comprando_artefato, cont_comprando_crystal]
    colors = ['#d4edda', '#f8d7da', '#fff3cd', '#fff3cd']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

    # Gráfico barras
    st.markdown("### Gráfico de Barras")

    fig2, ax2 = plt.subplots()
    ax2.bar(labels, sizes, color=colors)
    ax2.set_ylabel('Quantidade')
    ax2.set_ylim(0, max(sizes) + 2)

    for i, v in enumerate(sizes):
        ax2.text(i, v + 0.1, str(v), ha='center', fontweight='bold')

    st.pyplot(fig2)

# Exportação em ambas as abas
if st.button("📤 Exportar para Excel"):
    df.to_excel("dados.xlsx", index=False)
    st.success("Arquivo 'dados.xlsx' exportado com sucesso!")
    with open("dados.xlsx", "rb") as f:
        st.download_button(
            label="📥 Baixar dados.xlsx",
            data=f,
            file_name="dados.xlsx"
        )
