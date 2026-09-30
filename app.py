# Interface principal da aplicação de gestão de stock.

"""Este módulo apresenta o menu ao utilizador e chama as funções do módulo
stock.py para consultar, inserir e movimentar produtos.
"""

from datetime import date

import bd
import stock


def ler_inteiro(var, minimo=None):
    """Lê um número inteiro introduzido pelo utilizador.

    O valor é repetidamente solicitado até ser introduzido um número inteiro
    válido e, caso seja definido, maior ou igual ao valor mínimo.

    Args:
        var: texto apresentado ao utilizador no pedido de introdução. (string)
        minimo: valor mínimo permitido. (int, opcional)

    Returns:
        O número inteiro introduzido pelo utilizador.
    """
    while True:
        texto = input(var).strip()

        try:
            valor = int(texto)
        except ValueError:
            print(f"  '{texto}' não é um número inteiro.")
            continue

        if minimo is not None and valor < minimo:
            print(f"  Tem de ser pelo menos {minimo}.")
        else:
            return valor


def ler_preco(num):
    """Lê e converte um preço introduzido pelo utilizador.

    Aceita tanto a vírgula como o ponto como separador decimal.

    Args:
        num: texto apresentado ao utilizador no pedido do preço. (string)

    Returns:
        O preço convertido para float.
    """
    while True:
        texto = input(num).strip().replace(",", ".")

        try:
            return float(texto)
        except ValueError:
            print("  Escreve um valor, por exemplo 12,50.")


def euros(valor):
    """Converte um valor numérico para texto com formato monetário.

    O resultado apresenta duas casas decimais, espaço como separador
    de milhares e vírgula como separador decimal.

    Args:
        valor: valor numérico a formatar. (float)

    Returns:
        O valor formatado como texto monetário.
    """
    texto = f"{valor:,.2f}"
    return texto.replace(",", " ").replace(".", ",")


def listar():
    """Apresenta a lista de produtos existentes em stock.

    Mostra o código, o nome e a quantidade disponível de cada produto.
    Caso não existam produtos, apresenta uma mensagem informativa.

    Returns:
        None.
    """
    produtos = stock.listar_produtos()

    if not produtos:
        print("Ainda não há produtos.")
        return

    print(f"{'CÓDIGO':<8}{'PRODUTO':<15}{'QTD':>4}")

    for p in produtos:
        print(f"{p['codigo']:<8}{p['nome'][:14]:<15}{p['stock']:>4}")


def novo_produto():
    """Cria um novo produto através dos dados introduzidos pelo utilizador.

    Solicita o código, nome, preço e stock mínimo e envia esses dados
    para a função adicionar_produto() do módulo stock.

    Returns:
        None.

    Raises:
        ValueError: se os dados introduzidos não respeitarem as regras
            de validação definidas no módulo stock.
    """
    codigo = input("Código: ")
    nome = input("Nome: ")
    preco = ler_preco("Preço: ")
    minimo = ler_inteiro("Stock mínimo: ", minimo=0)

    stock.adicionar_produto(codigo, nome, preco, minimo)

    print("Produto criado com stock 0.")


def movimento(tipo):
    """Regista uma entrada ou saída de stock de um produto.

    Procura o produto pelo código, solicita a quantidade e uma nota
    opcional e regista o movimento através do módulo stock.

    Args:
        tipo: tipo de movimento a registar: "entrada" ou "saida". (string)

    Returns:
        None.

    Raises:
        ValueError: se o movimento não respeitar as regras de validação
            definidas no módulo stock.
    """
    produto = stock.procurar(input("Código: "))

    if produto is None:
        print("Esse código não existe. Usa a opção 1.")
        return

    print(f"{produto['nome']}: stock {produto['stock']}")

    quantidade = ler_inteiro("Quantidade: ", minimo=1)
    nota = input("Nota (pode ficar vazia): ").strip()

    novo = stock.registar_movimento(
        produto["codigo"], tipo, quantidade, nota
    )

    print(f"Registado. Stock agora: {novo}")


def alertas():
    """Apresenta os produtos que estão no mínimo ou abaixo dele.

    Consulta o módulo stock para obter os produtos que necessitam
    de reposição e apresenta o código, stock atual e stock mínimo.

    Returns:
        None.
    """
    lista = stock.em_falta()

    if not lista:
        print("Nenhum produto abaixo do mínimo.")

    for p in lista:
        print(f"{p['codigo']:<8} tem {p['stock']}, mínimo {p['minimo']}")


def historico():
    """Apresenta os últimos movimentos de um produto.

    Solicita o código do produto e apresenta os seus movimentos,
    indicando a data, a quantidade movimentada e a nota associada.

    Returns:
        None.
    """
    codigo = input("Código: ")
    linhas = stock.movimentos(codigo)

    if not linhas:
        print("Sem movimentos para esse código.")

    for m in linhas:
        sinal = "+" if m["tipo"] == "entrada" else "-"
        qtd = f"{sinal}{m['quantidade']}"
        print(f"{m['data']} {qtd:>4} {m['nota']}")


def mostrar_relatorio():
    """Apresenta um relatório geral do stock da aplicação.

    O relatório apresenta a data atual, o número de produtos,
    a quantidade em stock, o valor de cada produto, o valor total
    do stock e o número de produtos que estão no mínimo ou abaixo dele.

    Returns:
        None.
    """
    linhas, total = stock.relatorio()
    baixo = 0

    print("RELATÓRIO DE STOCK")
    print(f"{date.today():%d/%m/%Y} · {len(linhas)} produtos")
    print("=" * 25)
    print(f"{'PRODUTO':<13}{'QTD':>4}{'VALOR €':>8}")

    for p in linhas:
        alerta = ""

        if p["stock"] <= p["minimo"]:
            alerta = " !"
            baixo += 1

        print(
            f"{p['nome'][:13]:<13}{p['stock']:>4}"
            f"{euros(p['valor']):>8}{alerta}"
        )

    print("=" * 25)
    print(f"{'TOTAL':<17}{euros(total):>8}")
    print(f"! abaixo do mínimo: {baixo}")


def main():
    """Executa o menu principal da aplicação.

    Inicializa as tabelas da base de dados, carrega os produtos
    de exemplo quando a loja está vazia e apresenta o menu principal.
    O menu permanece ativo até o utilizador escolher a opção de saída.

    Returns:
        None.
    """
    bd.criar_tabelas()

    if stock.carregar_exemplo():
        print("Loja nova: 5 produtos de exemplo.")

    while True:
        print("\n===== GESTÃO DE STOCK =====")
        print("1 Listar     2 Novo produto")
        print("3 Entrada    4 Saída")
        print("5 Em falta   6 Histórico")
        print("7 Relatório  0 Sair")

        opcao = input("Opção: ").strip()

        try:
            if opcao == "1":
                listar()

            elif opcao == "2":
                novo_produto()

            elif opcao == "3":
                movimento("entrada")

            elif opcao == "4":
                movimento("saida")

            elif opcao == "5":
                alertas()

            elif opcao == "6":
                historico()

            elif opcao == "7":
                mostrar_relatorio()

            elif opcao == "0":
                print("Adeus!")
                break

            else:
                print("Opção inválida.")

        except ValueError as erro:
            print("Não foi possível:", erro)


main()
