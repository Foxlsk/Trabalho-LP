# Módulo de acesso à base de dados SQLite da aplicação.

"""Este ficheiro define o caminho da base de dados, o esquema das tabelas e o
contexto de ligação que garante que as operações são validadas e fechadas
corretamente.
"""

from contextlib import contextmanager
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "empresa.db")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    preco REAL NOT NULL CHECK (preco >= 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    minimo INTEGER NOT NULL CHECK (minimo >= 0)
);

CREATE TABLE IF NOT EXISTS movimentos (
    id INTEGER PRIMARY KEY,
    produto_id INTEGER REFERENCES produtos(id),
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data DATE NOT NULL,
    nota TEXT NOT NULL DEFAULT ''
);
"""


@contextmanager
def ligacao():
    """Cria uma ligação à base de dados SQLite.

    A ligação é utilizada como um gestor de contexto através de
    ``with ligacao() as con``. Desta forma, as operações são confirmadas
    quando terminam corretamente e anuladas caso ocorra uma exceção.

    Yields:
        sqlite3.Connection: ligação ativa à base de dados.

    Raises:
        sqlite3.Error: se ocorrer um erro durante a ligação ou durante
            uma operação na base de dados.
    """
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")

    try:
        with con:
            yield con
    finally:
        con.close()


def criar_tabelas():
    """Cria as tabelas da aplicação caso ainda não existam.

    A função executa o esquema definido na constante ``ESQUEMA``.
    Se as tabelas já existirem, não são recriadas nem alteradas.

    Returns:
        None.
    """
    with ligacao() as con:
        con.executescript(ESQUEMA)


criar_tabelas()

with ligacao() as con:
    tabelas = con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()

print("Base de dados:", DB_PATH)
print("Tabelas:", ", ".join(t["name"] for t in tabelas))
