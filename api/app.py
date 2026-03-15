from flask import Flask, request
import pandas as pd
import os

app = Flask(__name__)

CSV_FILE = os.path.join(os.getcwd(), "db_ideia.csv")

# senha vem do Vercel
SENHA_ADMIN = os.getenv("ADMIN_PASSWORD")


def carregar_dados():
    return pd.read_csv(CSV_FILE)


def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False)


@app.route("/")
def home():

    return """
    <html>
    <head>

    <title>Sistema de Estoque</title>

    <style>

    body{
        font-family:Arial;
        background:#0b0b0b;
        color:white;
        padding:40px;
    }

    h1{
        color:#ff7a00;
    }

    input{
        padding:12px;
        width:320px;
        border-radius:6px;
        border:none;
        background:#1a1a1a;
        color:white;
    }

    button{
        padding:12px 20px;
        background:#ff7a00;
        border:none;
        border-radius:6px;
        color:black;
        font-weight:bold;
        cursor:pointer;
    }

    button:hover{
        background:#ff8c1a;
    }

    .card{
        background:#161616;
        padding:20px;
        margin-top:20px;
        border-radius:10px;
        border-left:5px solid #ff7a00;
    }

    </style>

    </head>

    <body>

    <h1>📦 Sistema de Localização de Produtos</h1>

    <form action="/buscar">

        <input name="q" placeholder="Buscar por código ou nome">

        <button>Buscar</button>

    </form>

    </body>
    </html>
    """


@app.route("/buscar")
def buscar():

    q = request.args.get("q")

    df = carregar_dados()

    resultado = df[
        (df["ID_PRODUTO"].astype(str) == q) |
        (df["NOME_PRODUTO"].str.contains(q, case=False))
    ]

    if resultado.empty:
        return """
        <body style='background:#0b0b0b;color:white;font-family:Arial;padding:40px'>
        <h2>Produto não encontrado</h2>
        <a href="/" style="color:#ff7a00">Voltar</a>
        </body>
        """

    html = """
    <html>
    <head>

    <style>

    body{
        font-family:Arial;
        background:#0b0b0b;
        color:white;
        padding:40px;
    }

    a{
        color:#ff7a00;
        text-decoration:none;
    }

    .card{
        background:#161616;
        padding:20px;
        margin-top:20px;
        border-radius:10px;
        border-left:5px solid #ff7a00;
    }

    input{
        padding:8px;
        margin:5px;
        border-radius:6px;
        border:none;
        background:#1a1a1a;
        color:white;
    }

    button{
        padding:10px 15px;
        background:#ff7a00;
        border:none;
        border-radius:6px;
        color:black;
        font-weight:bold;
        cursor:pointer;
    }

    button:hover{
        background:#ff8c1a;
    }

    h2{
        color:#ff7a00;
    }

    </style>

    </head>

    <body>

    <a href="/">⬅ Voltar</a>
    """

    for _, row in resultado.iterrows():

        html += f"""
        <div class="card">

        <h2>{row["NOME_PRODUTO"]}</h2>

        <b>ID:</b> {row["ID_PRODUTO"]}<br>
        <b>Zona:</b> {row["ZONA"]}<br>
        <b>Corredor:</b> {row["CORREDOR"]}<br>
        <b>Fila:</b> {row["FILA"]}<br>
        <b>Posição:</b> {row["POSICAO"]}<br><br>

        <form action="/editar" method="post">

            <input type="hidden" name="id" value="{row["ID_PRODUTO"]}">

            Zona: <input name="zona"><br>
            Corredor: <input name="corredor"><br>
            Fila: <input name="fila"><br>
            Posição: <input name="posicao"><br>

            Senha: <input type="password" name="senha"><br><br>

            <button>Atualizar endereço</button>

        </form>

        </div>
        """

    html += "</body></html>"

    return html


@app.route("/editar", methods=["POST"])
def editar():

    senha = request.form["senha"]

    if senha != SENHA_ADMIN:

        return """
        <body style="background:#0b0b0b;color:white;font-family:Arial;padding:40px">

        <h2 style="color:red">Senha incorreta</h2>

        <a href="/" style="color:#ff7a00">Voltar</a>

        </body>
        """

    id_produto = int(request.form["id"])
    zona = request.form["zona"]
    corredor = request.form["corredor"]
    fila = request.form["fila"]
    posicao = request.form["posicao"]

    df = carregar_dados()

    df.loc[df["ID_PRODUTO"] == id_produto,
           ["ZONA","CORREDOR","FILA","POSICAO"]] = [
           zona, corredor, fila, posicao]

    salvar_dados(df)

    return """
    <body style="background:#0b0b0b;color:white;font-family:Arial;padding:40px">

    <h2 style="color:#ff7a00">Endereço atualizado com sucesso!</h2>

    <a href="/" style="color:#ff7a00">Voltar</a>

    </body>
    """


app = app