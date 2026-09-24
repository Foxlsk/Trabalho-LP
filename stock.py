"""Lógica de negócio da gestão de stock.

Este módulo não lê input nem imprime mensagens: apenas recebe dados, valida
regras e devolve resultados ao módulo de interface (app.py).
"""

import sqlite3
from datetime import date

from bd import ligacao

def adicionar_produto(codigo, nome, preco, minimo=0):
    """Cria um produto novo com stock inicial 0.

    Args:
        codigo: código único do produto.
        nome: nome visível do produto.
        preco: preço unitário.
        minimo: stock mínimo aconselhado para encomenda.

    Returns:
        O id do produto criado.

    Raises:
        ValueError: se o código, o nome ou os valores forem inválidos.
    """
    codigo = codigo.strip().upper()
    nome = nome.strip()
    if not codigo or not nome:
        raise ValueError("o código e o nome são obrigatórios")
    if preco < 0 or minimo < 0:
        raise ValueError("o preço e o mínimo não podem ser negativos")
    try:
        with ligacao() as con:
            cur = con.execute(
                "INSERT INTO produtos (codigo, nome, preco, stock, minimo) "
                "VALUES (?, ?, ?, ?, ?)",
                (codigo, nome, preco, 0, minimo),
            )
    except sqlite3.IntegrityError:
        raise ValueError(f"já existe um produto {codigo}") from None
    return cur.lastrowid

def procurar(codigo):
    """Devolve um produto pelo código, ou None se não existir."""
    with ligacao() as con:
        return con.execute(
            "SELECT * FROM produtos WHERE codigo = ?",
            (codigo.strip().upper(),),
        ).fetchone()

def listar_produtos():
    """Devolve todos os produtos ordenados por código."""
    with ligacao() as con:
        return con.execute(
            "SELECT * FROM produtos ORDER BY codigo"
        ).fetchall()

def registar_movimento(codigo, tipo, quantidade, nota=""):
    """Regista uma entrada ou saída de stock.

    Args:
        codigo: código do produto.
        tipo: "entrada" ou "saida".
        quantidade: número de unidades do movimento.
        nota: texto opcional sobre o movimento.

    Returns:
        O stock final do produto após o movimento.

    Raises:
        ValueError: se o tipo, a quantidade ou o stock forem inválidos.
    """
    if tipo not in ("entrada", "saida"):
        raise ValueError("o tipo tem de ser entrada ou saida")
    if quantidade <= 0:
        raise ValueError("a quantidade tem de ser maior que zero")

    produto = procurar(codigo)
    if produto is None:
        raise ValueError(f"não existe o produto {codigo}")

    variacao = quantidade if tipo == "entrada" else -quantidade
    novo_stock = produto["stock"] + variacao
    if novo_stock < 0:
        raise ValueError(
            f"stock insuficiente, {produto['nome']} tem {produto['stock']}"
        )

    with ligacao() as con:
        con.execute(
            "INSERT INTO movimentos "
            "(produto_id, tipo, quantidade, data, nota) "
            "VALUES (?, ?, ?, ?, ?)",
            (produto["id"], tipo, quantidade,
             date.today().isoformat(), nota),
        )
        con.execute(
            "UPDATE produtos SET stock = stock + ? WHERE id = ?",
            (variacao, produto["id"]),
        )

    return novo_stock

def em_falta():
    """Devolve os produtos com stock igual ou abaixo do mínimo."""
    with ligacao() as con:
        return con.execute(
            "SELECT codigo, nome, stock, minimo FROM produtos "
            "WHERE stock <= minimo ORDER BY stock - minimo, codigo"
        ).fetchall()

def movimentos(codigo, limite=5):
    """Devolve os últimos movimentos de um produto, do mais recente para o mais antigo."""
    with ligacao() as con:
        return con.execute(
            "SELECT m.data, m.tipo, m.quantidade, m.nota "
            "FROM movimentos AS m "
            "JOIN produtos AS p ON p.id = m.produto_id "
            "WHERE p.codigo = ? ORDER BY m.id DESC LIMIT ?",
            (codigo.strip().upper(), limite),
        ).fetchall()

def relatorio():
    """Devolve as linhas do relatório e o valor total em stock."""
    with ligacao() as con:
        linhas = con.execute(
            "SELECT codigo, nome, stock, minimo, "
            "stock * preco AS valor FROM produtos ORDER BY nome"
        ).fetchall()
    total = sum(p["valor"] for p in linhas)
    return linhas, total

PRODUTOS = [
    # código, nome, preço, mínimo, stock inicial
    ("RATO-01", "Rato sem fios", 14.90, 5, 12),
    ("TECL-02", "Teclado USB", 20.00, 5, 3),
    ("PEN-64", "Pen USB 64 GB", 9.50, 8, 0),
    ("HDMI-2M", "Cabo HDMI 2 m", 6.90, 10, 25),
    ("MON-24", 'Monitor 24"', 129.00, 2, 4),
]

def carregar_exemplo():
    """Cria os produtos de exemplo se a loja estiver vazia."""
    if listar_produtos():
        return False
    for codigo, nome, preco, minimo, inicial in PRODUTOS:
        adicionar_produto(codigo, nome, preco, minimo)
        if inicial > 0:
            registar_movimento(codigo, "entrada", inicial, "stock inicial")
    return True



print("stock.py é um módulo: só define funções.")
print("Executa o teste_stock.py ou o app.py.")