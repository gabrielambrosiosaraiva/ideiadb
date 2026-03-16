import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(__file__)
CSV_FILE = os.path.join(BASE_DIR, "db_ideia.csv")
SENHA_ADMIN = os.getenv("ADMIN_PASSWORD")  # senha do Streamlit Cloud

# --- FUNÇÕES ---
def carregar_dados():
    """Lê o CSV e retorna o DataFrame"""
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # Cria um CSV vazio se não existir
        df = pd.DataFrame(columns=["ID_PRODUTO", "NOME_PRODUTO", "ZONA", "CORREDOR", "FILA", "POSICAO"])
        df.to_csv(CSV_FILE, index=False)
        return df

def salvar_dados(df):
    """Salva o DataFrame no CSV"""
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
st.write("Busque e edite produtos facilmente.")

# --- CARREGA DADOS ---
df = carregar_dados()

# --- CAMPO DE BUSCA ---
q = st.text_input("Buscar por código ou nome:")

resultado = pd.DataFrame()
if q:
    if q.isdigit():
        # Busca exata por ID
        resultado = df[df["ID_PRODUTO"].astype(str) == q]
    else:
        # Busca por nome parcial
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
                                df.loc[df["ID_PRODUTO"] == row["ID_PRODUTO"], ["ZONA","CORREDOR","FILA","POSICAO"]] = [
                                    zona, corredor, fila, posicao
                                ]
                                salvar_dados(df)
                                st.success("Endereço atualizado com sucesso!")
                                st.experimental_rerun()  # Recarrega para mostrar as mudanças imediatamente
