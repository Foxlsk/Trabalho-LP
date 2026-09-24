"""Módulo de acesso à base de dados SQLite da aplicação.

Este ficheiro define o caminho da base de dados, o esquema das tabelas e o
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
    """Abre uma ligação SQLite e garante commit/rollback no fim.

    O bloco ``with ligacao() as con`` garante que:
    - a ligação fica aberta durante a operação;
    - os dados são guardados se tudo correr bem;
    - tudo é anulado em caso de erro;
    - a ligação fechada mesmo se ocorrer exceção.
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
    """Cria as tabelas do sistema, se ainda não existirem."""
    with ligacao() as con:
        con.executescript(ESQUEMA)




criar_tabelas()
with ligacao() as con:
    tabelas = con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
print("Base de dados:", DB_PATH)
print("Tabelas:", ", ".join(t["name"] for t in tabelas))
