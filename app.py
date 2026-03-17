import streamlit as st
import pandas as pd
import os


BASE_DIR = os.path.dirname(__file__)
CSV_FILE = os.path.join(BASE_DIR, "db_ideia.csv")
SENHA_ADMIN = os.getenv("ADMIN_PASSWORD")  # senha do Streamlit Cloud


def carregar_dados():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["ID_PRODUTO","NOME_PRODUTO","ZONA","CORREDOR","FILA","POSICAO"])
        df.to_csv(CSV_FILE, index=False)
        return df

def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False)


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


st.title("📦 Sistema de Localização de Produtos")
st.write("Busque e edite produtos facilmente.")


df = carregar_dados()


q = st.text_input("Buscar por código ou nome:")

resultado = pd.DataFrame()
if q:
    if q.isdigit():
        resultado = df[df["ID_PRODUTO"].astype(str) == q]
    else:
        resultado = df[df["NOME_PRODUTO"].str.contains(q, case=False)]

    if resultado.empty:
        st.warning("Produto não encontrado")
    else:
        for idx, row in resultado.iterrows():
          
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

          
            key_expander = f"expander_{row['ID_PRODUTO']}"
            with st.expander("Editar endereço", expanded=False, key=key_expander):
                senha_key = f"senha_{row['ID_PRODUTO']}"
                if senha_key not in st.session_state:
                    st.session_state[senha_key] = ""
                senha_input = st.text_input("Digite a senha para editar:", type="password", key=senha_key)
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
                                    zona, corredor, fila, posicao
                                ]
                                salvar_dados(df)
                                st.success("Endereço atualizado com sucesso!")
                                
                                df = carregar_dados()

st.header("➕ Adicionar novo produto")

with st.expander("Clique aqui para adicionar um produto"):
    with st.form("form_add_produto"):
        novo_id = st.text_input("ID do Produto")
        novo_nome = st.text_input("Nome do Produto")
        nova_zona = st.text_input("Zona")
        novo_corredor = st.text_input("Corredor")
        nova_fila = st.text_input("Fila")
        nova_posicao = st.text_input("Posição")

        adicionar = st.form_submit_button("Adicionar produto")

        if adicionar:
            if not novo_id or not novo_nome:
                st.error("ID e Nome do produto são obrigatórios.")
            elif novo_id in df["ID_PRODUTO"].astype(str).values:
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
                df = pd.concat([df, pd.DataFrame([novo_produto])], ignore_index=True)
                salvar_dados(df)
                st.success(f"Produto '{novo_nome}' adicionado com sucesso!")



