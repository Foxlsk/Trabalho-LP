import sqlite3
from datetime import date

from bd import ligacao


def adicionar_produto(codigo, nome, preco, minimo=0):
    """Cria um produto novo com stock inicial 0.

    Args:
        codigo: código único do produto. (string)
        nome: nome visível do produto. (string)
        preco: preço unitário. (float)
        minimo: stock mínimo aconselhado para encomenda. (int)

    Returns:
        O id do produto criado.

    Raises:
        ValueError: se o código ou nome estiverem vazios, ou se
            o preço ou mínimo forem negativos.
        ValueError: se já existir um produto com o mesmo código.
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
    """Procura um produto pelo seu código.

    Args:
        codigo: código do produto a procurar. (string)

    Returns:
        O produto encontrado ou None caso não exista.
    """
    with ligacao() as con:
        return con.execute(
            "SELECT * FROM produtos WHERE codigo = ?",
            (codigo.strip().upper(),),
        ).fetchone()


def listar_produtos():
    """Devolve todos os produtos existentes.

    Returns:
        Uma lista com todos os produtos, ordenados por código.
    """
    with ligacao() as con:
        return con.execute(
            "SELECT * FROM produtos ORDER BY codigo"
        ).fetchall()


def registar_movimento(codigo, tipo, quantidade, nota=""):
    """Regista uma entrada ou saída de stock.

    Args:
        codigo: código do produto.
        tipo: tipo de movimento: "entrada" ou "saida".
        quantidade: número de unidades do movimento.
        nota: texto opcional sobre o movimento.

    Returns:
        O stock final do produto após o movimento.

    Raises:
        ValueError: se o tipo de movimento for inválido.
        ValueError: se a quantidade for menor ou igual a zero.
        ValueError: se o produto não existir.
        ValueError: se não houver stock suficiente para uma saída.
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
    """Procura os produtos cujo stock está igual ou abaixo do mínimo.

    Returns:
        Uma lista com o código, nome, stock atual e stock mínimo
        dos produtos que precisam de reposição.
    """
    with ligacao() as con:
        return con.execute(
            "SELECT codigo, nome, stock, minimo FROM produtos "
            "WHERE stock <= minimo ORDER BY stock - minimo, codigo"
        ).fetchall()


def movimentos(codigo, limite=5):
    """Devolve os movimentos mais recentes de um produto.

    Args:
        codigo: código do produto.
        limite: número máximo de movimentos a devolver. (int)

    Returns:
        Uma lista dos movimentos do produto, do mais recente
        para o mais antigo.
    """
    with ligacao() as con:
        return con.execute(
            "SELECT m.data, m.tipo, m.quantidade, m.nota "
            "FROM movimentos AS m "
            "JOIN produtos AS p ON p.id = m.produto_id "
            "WHERE p.codigo = ? ORDER BY m.id DESC LIMIT ?",
            (codigo.strip().upper(), limite),
        ).fetchall()


def relatorio():
    """Gera um relatório dos produtos e do valor total em stock.

    Returns:
        Uma tupla com dois elementos:
        - linhas: lista com código, nome, stock, mínimo e valor em stock.
        - total: valor total de todos os produtos em stock.
    """
    with ligacao() as con:
        linhas = con.execute(
            "SELECT codigo, nome, stock, minimo, "
            "stock * preco AS valor FROM produtos ORDER BY nome"
        ).fetchall()

    total = sum(p["valor"] for p in linhas)
    return linhas, total


PRODUTOS = [
    # Código, nome, preço, mínimo, stock inicial.
    ("RATO-01", "Rato sem fios", 14.90, 5, 12),
    ("TECL-02", "Teclado USB", 20.00, 5, 3),
    ("PEN-64", "Pen USB 64 GB", 9.50, 8, 0),
    ("HDMI-2M", "Cabo HDMI 2 m", 6.90, 10, 25),
    ("MON-24", 'Monitor 24"', 129.00, 2, 4),
]


def carregar_exemplo():
    """Cria os produtos de exemplo caso a loja esteja vazia.

    Os produtos são adicionados com stock inicial igual a zero
    e, quando aplicável, é registado um movimento de entrada
    correspondente ao stock inicial.

    Returns:
        True se os produtos de exemplo forem carregados.
        False se a loja já tiver produtos.
    """
    if listar_produtos():
        return False

    for codigo, nome, preco, minimo, inicial in PRODUTOS:
        adicionar_produto(codigo, nome, preco, minimo)

        if inicial > 0:
            registar_movimento(
                codigo,
                "entrada",
                inicial,
                "stock inicial"
            )

    return True