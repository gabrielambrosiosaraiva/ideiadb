import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(__file__)
CSV_FILE = os.path.join(BASE_DIR, "db_ideia.csv")
SENHA_ADMIN = os.getenv("ADMIN_PASSWORD")  # pega do ambiente, sem fallback

if not SENHA_ADMIN:
    st.error("⚠️ ADMIN_PASSWORD não está definido no ambiente do Streamlit.")
    st.stop()

# --- FUNÇÕES ---
@st.cache_data
def carregar_dados():
    return pd.read_csv(CSV_FILE)

def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False)

# --- ESTILO ---
st.set_page_config(page_title="Sistema de Estoque", layout="wide")
st.markdown("""
<style>
body {background-color: #0b0b0b; color: white; font-family: Arial, sans-serif;}
.stTextInput>div>div>input {background-color: #1a1a1a; color: white; border-radius:6px; padding:10px;}
.stButton>button {background-color:#ff7a00; color:black; font-weight:bold; border-radius:6px; padding:10px 20px;}
.stButton>button:hover {background-color:#ff8c1a;}
.card {background-color:#161616; padding:20px; margin-top:20px; border-radius:10px; border-left:5px solid #ff7a00;}
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.title("📦 Sistema de Localização de Produtos")
st.write("Busque, edite ou crie produtos facilmente.")

# --- CAMPO DE BUSCA ---
q = st.text_input("Buscar por código ou nome:")

if q:
    df = carregar_dados()
    resultado = df[
        (df["ID_PRODUTO"].astype(str) == q) |
        (df["NOME_PRODUTO"].str.contains(q, case=False))
    ]

    if resultado.empty:
        st.warning("Produto não encontrado")
    else:
        for _, row in resultado.iterrows():
            st.markdown(f"""
            <div class="card">
            <h2>{row['NOME_PRODUTO']}</h2>
            <b>ID:</b> {row['ID_PRODUTO']}<br>
            <b>Zona:</b> {row['ZONA']}<br>
            <b>Corredor:</b> {row['CORREDOR']}<br>
            <b>Fila:</b> {row['FILA']}<br>
            <b>Posição:</b> {row['POSICAO']}<br>
            </div>
            """, unsafe_allow_html=True)

            # --- BOTÃO EDITAR ---
            if st.button(f"Editar {row['ID_PRODUTO']}", key=f"editar_{row['ID_PRODUTO']}"):
                senha_input = st.text_input("Digite a senha para editar:", type="password", key=f"senha_{row['ID_PRODUTO']}")
                if senha_input:
                    if senha_input != SENHA_ADMIN:
                        st.error("Senha incorreta")
                    else:
                        st.success("Senha correta! Agora você pode atualizar o endereço.")
                        with st.form(f"form_{row['ID_PRODUTO']}"):
                            zona = st.text_input("Zona", value=row['ZONA'], key=f"zona_{row['ID_PRODUTO']}")
                            corredor = st.text_input("Corredor", value=row['CORREDOR'], key=f"corredor_{row['ID_PRODUTO']}")
                            fila = st.text_input("Fila", value=row['FILA'], key=f"fila_{row['ID_PRODUTO']}")
                            posicao = st.text_input("Posição", value=row['POSICAO'], key=f"posicao_{row['ID_PRODUTO']}")
                            atualizar = st.form_submit_button("Atualizar endereço")
                            if atualizar:
                                df.loc[df["ID_PRODUTO"] == row["ID_PRODUTO"],
                                       ["ZONA","CORREDOR","FILA","POSICAO"]] = [
                                       zona, corredor, fila, posicao]
                                salvar_dados(df)
                                st.success("Endereço atualizado com sucesso!")

# --- CRIAR PRODUTO NOVO COM SENHA ---
st.subheader("➕ Criar Produto Novo")

senha_novo = st.text_input("Digite a senha para criar novo produto:", type="password", key="senha_novo")
if senha_novo:
    if senha_novo != SENHA_ADMIN:
        st.error("Senha incorreta")
    else:
        st.success("Senha correta! Preencha os campos abaixo para criar o produto.")
        with st.form("form_novo"):
            id_produto = st.text_input("ID Produto", key="novo_id")
            nome_produto = st.text_input("Nome Produto", key="novo_nome")
            zona = st.text_input("Zona", key="novo_zona")
            corredor = st.text_input("Corredor", key="novo_corredor")
            fila = st.text_input("Fila", key="novo_fila")
            posicao = st.text_input("Posição", key="novo_posicao")
            criar = st.form_submit_button("Criar Produto")
            if criar:
                df = carregar_dados()
                if int(id_produto) in df["ID_PRODUTO"].values:
                    st.error("ID já existe! Escolha outro.")
                else:
                    novo_item = pd.DataFrame([{
                        "ID_PRODUTO": int(id_produto),
                        "NOME_PRODUTO": nome_produto,
                        "ZONA": zona,
                        "CORREDOR": corredor,
                        "FILA": fila,
                        "POSICAO": posicao
                    }])
                    df = pd.concat([df, novo_item], ignore_index=True)
                    salvar_dados(df)
                    st.success(f"Produto {nome_produto} criado com sucesso!")
