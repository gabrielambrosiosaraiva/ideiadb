import streamlit as st
import pandas as pd
import os
import requests, base64
from io import StringIO

GITHUB_REPO = "gabrielambrosiosaraiva/ideiadb"
GITHUB_FILE = "db_ideia.csv"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SENHA_ADMIN = os.getenv("ADMIN_PASSWORD", "admin")

def carregar_dados():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode()
        df = pd.read_csv(StringIO(content))
        return df.astype(str)
    else:
        return pd.DataFrame(columns=["ID_PRODUTO","NOME_PRODUTO","ZONA","CORREDOR","FILA","POSICAO"])

def salvar_dados(df):
    csv_content = df.to_csv(index=False)
    b64_content = base64.b64encode(csv_content.encode()).decode()

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    r = requests.get(url, headers=headers)
    sha = r.json()["sha"] if r.status_code == 200 else None

    payload = {
        "message": "Atualização automática do CSV pelo Streamlit",
        "content": b64_content,
        "sha": sha
    }

    r = requests.put(url, json=payload, headers=headers)
    if r.status_code in [200, 201]:
        st.success("Atualizado com sucesso!")
    else:
        st.error(f"Erro ao atualizar. Contato o Administrador: {r.text}")

st.set_page_config(page_title="GPS_Ideia", layout="wide")

st.markdown("""
<h1 style='text-align: center; font-size: 60px; margin-bottom: 0;'>📦 GPS_Ideia</h1>
<h3 style='text-align: center; color: gray; margin-top: 5px;'>Galpão Position System</h3>
""", unsafe_allow_html=True)

df = carregar_dados()

if "novos_produtos" not in st.session_state:
    st.session_state["novos_produtos"] = []

col_busca1, col_busca2, col_busca3 = st.columns(3)

with col_busca1:
    q = st.text_input("Buscar por código ou nome:")

with col_busca2:
    busca_corredor = st.text_input("Corredor:")

with col_busca3:
    busca_fila = st.text_input("Fila:")

resultado = pd.DataFrame()

if busca_fila and not busca_corredor:
    st.warning("Para buscar por fila, informe também o corredor.")
else:
    resultado = df.copy()

    if q:
        if q.isdigit():
            resultado = resultado[resultado["ID_PRODUTO"] == q]
        else:
            resultado = resultado[resultado["NOME_PRODUTO"].str.contains(q, case=False, na=False)]

    if busca_corredor:
        resultado = resultado[resultado["CORREDOR"].str.contains(busca_corredor, case=False, na=False)]

    if busca_fila:
        resultado = resultado[resultado["FILA"].str.contains(busca_fila, case=False, na=False)]

if q or busca_corredor or busca_fila:
    if resultado.empty:
        st.warning("Produto não encontrado")
    else:
        for idx, row in resultado.iterrows():

            if busca_fila or busca_corredor:
                st.markdown(f"""
                <div style="background:#1e1e1e;color:white;padding:8px;margin-top:5px;border-radius:6px;border-left:3px solid #ff7a00;font-size:13px;">
                <b>{row['NOME_PRODUTO']}</b> | 
                ID: {row['ID_PRODUTO']} | 
                Z: {row['ZONA']} | 
                C: {row['CORREDOR']} | 
                F: {row['FILA']} | 
                P: {row['POSICAO']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#161616;color:white;padding:15px;margin-top:10px;border-radius:8px;border-left:5px solid #ff7a00;">
                <h3>{row['NOME_PRODUTO']}</h3>
                <b>ID:</b> {row['ID_PRODUTO']}<br>
                <b>Zona:</b> {row['ZONA']}<br>
                <b>Corredor:</b> {row['CORREDOR']}<br>
                <b>Fila:</b> {row['FILA']}<br>
                <b>Posição:</b> {row['POSICAO']}<br>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Editar endereço", expanded=False):
                senha_input = st.text_input("Digite a senha para editar:", type="password", key=f"senha_{row['ID_PRODUTO']}_{idx}")
                if senha_input:
                    if senha_input != SENHA_ADMIN:
                        st.error("Senha incorreta")
                    else:
                        with st.form(f"form_{row['ID_PRODUTO']}"):
                            zona = st.text_input("Zona", value=row['ZONA'])
                            corredor = st.text_input("Corredor", value=row['CORREDOR'])
                            fila = st.text_input("Fila", value=row['FILA'])
                            posicao = st.text_input("Posição", value=row['POSICAO'])
                            atualizar = st.form_submit_button("Atualizar endereço")
                            if atualizar:
                                df.loc[df["ID_PRODUTO"] == row["ID_PRODUTO"],
                                       ["ZONA","CORREDOR","FILA","POSICAO"]] = [
                                    zona, corredor, fila, posicao
                                ]
                                salvar_dados(df)
                                st.success("Endereço atualizado com sucesso!")

col1, col2 = st.columns([3,1])
with col1:
    st.markdown("""
    <h4 style='margin-bottom:0;'>➕ Novos produtos</h4>
    """, unsafe_allow_html=True)
with col2:
    if st.button("💾 Salvar alterações"):
        if st.session_state["novos_produtos"]:
            df = pd.concat([df, pd.DataFrame(st.session_state["novos_produtos"])], ignore_index=True)
            salvar_dados(df)
            st.session_state["novos_produtos"] = []
            st.success("Alterações salvas!")
        else:
            st.warning("Não há produtos para salvar.")

if "logado_add" not in st.session_state:
    st.session_state["logado_add"] = False

if not st.session_state["logado_add"]:
    senha_add = st.text_input("Senha de administrador:", type="password")
    if senha_add == SENHA_ADMIN:
        st.session_state["logado_add"] = True
        st.success("Login realizado! Agora você pode adicionar produtos.")
    elif senha_add:
        st.error("Senha incorreta")

if st.session_state["logado_add"]:
    with st.form("form_add_produto"):
        novo_id = st.text_input("ID do Produto")
        novo_nome = st.text_input("Nome do Produto")
        nova_zona = st.text_input("Zona")
        novo_corredor = st.text_input("Corredor")
        nova_fila = st.text_input("Fila")
        nova_posicao = st.text_input("Posição")

        adicionar = st.form_submit_button("Adicionar à lista")

        if adicionar:
            if not novo_id or not novo_nome:
                st.error("ID e Nome do produto são obrigatórios.")
            elif novo_id in df["ID_PRODUTO"].values:
                st.error("Já existe um produto com esse ID.")
            else:
                novo_produto = {
                    "ID_PRODUTO": novo_id,
                    "NOME_PRODUTO": novo_nome,
                    "ZONA": nova_zona,
                    "CORREDOR": novo_corredor,
                    "FILA": nova_fila,
                    "POSICAO": nova_posicao
                }
                st.session_state["novos_produtos"].append(novo_produto)
                st.success(f"Produto '{novo_nome}' adicionado à lista (pendente de salvar).")

if st.session_state["novos_produtos"]:
    st.subheader("📋 Produtos adicionados (pendentes)")
    st.table(pd.DataFrame(st.session_state["novos_produtos"]))
