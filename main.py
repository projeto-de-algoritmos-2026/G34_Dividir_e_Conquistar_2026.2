import time

from filmes import carregar_filmes
from buscas import (
    busca_sequencial,
    busca_binaria,
    busca_interpolacao,
    montar_arvore_balanceada,
    TabelaHash,
    tamanho_recomendado_para_hash,
)
from ordenacoes import (
    selection_sort,
    insertion_sort,
    bubble_sort,
    counting_sort,
    radix_sort,
    heap_sort,
)

# quantas ocorrências uma busca por trecho (título/gênero) devolve no
# máximo -- ela para de procurar assim que atingir esse número.
LIMITE_BUSCA_POR_TRECHO = 10

CAMPOS = {
    "1": {
        "id": "codigo",
        "nome": "Código",
        "chave": lambda f: f.codigo,
        "conversor": int,
        "unico": True,
        "numerico": True,
        "modo": "igual",
        "limite": None,
    },
    "2": {
        "id": "titulo",
        "nome": "Título",
        "chave": lambda f: f.titulo.casefold(),
        "conversor": lambda texto: texto.casefold(),
        "unico": False,
        "numerico": False,
        "modo": "contem",
        "limite": LIMITE_BUSCA_POR_TRECHO,
    },
    "3": {
        "id": "ano",
        "nome": "Ano",
        "chave": lambda f: f.ano,
        "conversor": int,
        "unico": False,
        "numerico": True,
        "modo": "igual",
        "limite": None,
    },
    "4": {
        "id": "genero",
        "nome": "Gênero",
        "chave": lambda f: f.genero.casefold(),
        "conversor": lambda texto: texto.casefold(),
        "unico": False,
        "numerico": False,
        "modo": "contem",
        "limite": LIMITE_BUSCA_POR_TRECHO,
    },
}

METODOS = {
    "1": "Busca Sequencial",
    "2": "Busca Binária",
    "3": "Busca por Interpolação",
    "4": "Busca em Árvore Binária",
    "5": "Busca por Hashing",
}

# "apenas_numerico": counting/radix indexam um vetor pelo valor da chave,
# então só funcionam com chaves inteiras (código e ano).
ALGORITMOS_ORDENACAO = {
    "1": {"nome": "Selection Sort", "funcao": selection_sort, "apenas_numerico": False},
    "2": {"nome": "Insertion Sort", "funcao": insertion_sort, "apenas_numerico": False},
    "3": {"nome": "Bubble Sort", "funcao": bubble_sort, "apenas_numerico": False},
    "4": {"nome": "Counting Sort", "funcao": counting_sort, "apenas_numerico": True},
    "5": {"nome": "Radix Sort", "funcao": radix_sort, "apenas_numerico": True},
    "6": {"nome": "Heap Sort", "funcao": heap_sort, "apenas_numerico": False},
}


def campos_disponiveis(metodo_id):
    return CAMPOS


def montar_estruturas(filmes):
    estruturas = {}
    tamanho_hash = tamanho_recomendado_para_hash(len(filmes))
    for campo in CAMPOS.values():
        chave = campo["chave"]
        # vetor ordenado usado pela busca binária / interpolação, agora
        # gerado pelo nosso Heap Sort (O(n log n)) em vez do sorted() do Python
        ordenados, _, _ = heap_sort(filmes, chave=chave)

        arvore = montar_arvore_balanceada(ordenados, chave=chave)

        tabela_hash = TabelaHash(tamanho=tamanho_hash, chave=chave)
        for filme in filmes:
            tabela_hash.inserir(filme)

        estruturas[campo["id"]] = {
            "ordenados": ordenados,
            "arvore": arvore,
            "hash": tabela_hash,
        }
    return estruturas


def executar_busca(metodo_id, campo, valor, filmes, estruturas):
    chave = campo["chave"]
    dados = estruturas[campo["id"]]

    if campo["modo"] == "contem":
        limite = campo["limite"]
        if metodo_id == "1":
            return busca_sequencial(filmes, valor, chave=chave, modo="contem", limite=limite)
        if metodo_id in ("2", "3"):
            return busca_sequencial(dados["ordenados"], valor, chave=chave, modo="contem", limite=limite)
        if metodo_id == "4":
            return dados["arvore"].buscar_por_trecho(valor, limite=limite)
        if metodo_id == "5":
            return dados["hash"].buscar_por_trecho(valor, limite=limite)
        raise ValueError(f"Método de busca desconhecido: {metodo_id}")

    if metodo_id == "1":
        return busca_sequencial(filmes, valor, chave=chave, chave_unica=campo["unico"])
    if metodo_id == "2":
        return busca_binaria(dados["ordenados"], valor, chave=chave)
    if metodo_id == "3":
        return busca_interpolacao(dados["ordenados"], valor, chave=chave)
    if metodo_id == "4":
        return dados["arvore"].buscar(valor)
    if metodo_id == "5":
        return dados["hash"].buscar(valor)
    raise ValueError(f"Método de busca desconhecido: {metodo_id}")


def listar_catalogo(filmes):
    print("\n--- Catálogo de filmes (ordenado por código) ---")
    for filme in sorted(filmes, key=lambda f: f.codigo):
        print(" ", filme)
    print()


def ler_valor_busca(campo):
    rotulo = campo["nome"] + (" (contém)" if campo["modo"] == "contem" else "")
    while True:
        entrada = input(f"{rotulo} (Enter para voltar): ").strip()
        if entrada == "":
            return None
        try:
            return campo["conversor"](entrada)
        except ValueError:
            print("Valor inválido para este campo.\n")


LIMITE_RESULTADOS_EXIBIDOS = 20


def buscar_no_submenu(metodo_id, metodo_nome, campo, filmes, estruturas):
    print(f"\n--- {metodo_nome} | Campo: {campo['nome']} ---")
    print(f"({len(filmes)} filmes no catálogo -- use a opção 6 do menu principal pra ver a lista completa)\n")

    while True:
        valor = ler_valor_busca(campo)
        if valor is None:
            break

        inicio = time.perf_counter()
        encontrados, comparacoes = executar_busca(metodo_id, campo, valor, filmes, estruturas)
        fim = time.perf_counter()

        if encontrados:
            print(f"{len(encontrados)} filme(s) encontrado(s):")
            for filme in encontrados[:LIMITE_RESULTADOS_EXIBIDOS]:
                print(" ", filme)
            excedente = len(encontrados) - LIMITE_RESULTADOS_EXIBIDOS
            if excedente > 0:
                print(f"  ... e mais {excedente} filme(s) (não exibidos).")
        else:
            print("Nenhum filme encontrado.")
        print(f"Comparações: {comparacoes} | Tempo: {(fim - inicio) * 1000:.4f} ms\n")


def comparar_metodos(filmes, estruturas):
    campo = CAMPOS["1"]
    codigos_existentes = [f.codigo for f in filmes]
    codigo_inexistente = max(codigos_existentes) + 1

    print("\n--- Comparativo de desempenho (busca por código) ---")
    print(f"{len(codigos_existentes)} buscas bem-sucedidas (uma por filme do catálogo)\n")
    cabecalho = (f"{'Método':<26}{'Melhor':>8}{'Pior':>8}{'Médio':>10}"
                 f"{'Malsucedida':>13}{'Tempo total (ms)':>18}")
    print(cabecalho)
    print("-" * len(cabecalho))

    for metodo_id, nome in METODOS.items():
        comparacoes_lista = []

        inicio = time.perf_counter()
        for codigo in codigos_existentes:
            _, comparacoes = executar_busca(metodo_id, campo, codigo, filmes, estruturas)
            comparacoes_lista.append(comparacoes)
        _, comparacoes_ausente = executar_busca(metodo_id, campo, codigo_inexistente, filmes, estruturas)
        fim = time.perf_counter()

        melhor = min(comparacoes_lista)
        pior = max(comparacoes_lista)
        media = sum(comparacoes_lista) / len(comparacoes_lista)
        tempo_total_ms = (fim - inicio) * 1000

        print(f"{nome:<26}{melhor:>8}{pior:>8}{media:>10.2f}"
              f"{comparacoes_ausente:>13}{tempo_total_ms:>18.4f}")
    print()


def menu_campo(metodo_id, metodo_nome, filmes, estruturas):
    campos = campos_disponiveis(metodo_id)

    while True:
        print(f"\n--- {metodo_nome}: buscar por qual campo? ---")
        for chave_menu, campo in campos.items():
            print(f"{chave_menu} - {campo['nome']}")
        print("0 - Voltar ao menu principal")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            return
        if escolha not in campos:
            print("Opção inválida!\n")
            continue

        buscar_no_submenu(metodo_id, metodo_nome, campos[escolha], filmes, estruturas)


def campos_para_ordenacao(algoritmo):
    if algoritmo["apenas_numerico"]:
        return {k: c for k, c in CAMPOS.items() if c["numerico"]}
    return CAMPOS


def ordenar_catalogo(algoritmo, campo, filmes):
    print(f"\n--- {algoritmo['nome']} | Campo: {campo['nome']} ---")
    inicio = time.perf_counter()
    ordenados, comparacoes, movimentacoes = algoritmo["funcao"](filmes, chave=campo["chave"])
    fim = time.perf_counter()

    print(f"Primeiros {LIMITE_RESULTADOS_EXIBIDOS} de {len(ordenados)} filmes ordenados:")
    for filme in ordenados[:LIMITE_RESULTADOS_EXIBIDOS]:
        print(" ", filme)
    print(f"Comparações: {comparacoes} | Movimentações: {movimentacoes} | "
          f"Tempo: {(fim - inicio) * 1000:.4f} ms\n")


def menu_ordenacao(filmes):
    while True:
        print("\n--- Ordenar catálogo: qual algoritmo? ---")
        for chave_menu, algoritmo in ALGORITMOS_ORDENACAO.items():
            print(f"{chave_menu} - {algoritmo['nome']}")
        print("0 - Voltar ao menu principal")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            return
        if escolha not in ALGORITMOS_ORDENACAO:
            print("Opção inválida!\n")
            continue

        algoritmo = ALGORITMOS_ORDENACAO[escolha]
        campos = campos_para_ordenacao(algoritmo)
        if algoritmo["apenas_numerico"]:
            print(f"({algoritmo['nome']} só ordena chaves inteiras)")

        print(f"\n--- {algoritmo['nome']}: ordenar por qual campo? ---")
        for chave_menu, campo in campos.items():
            print(f"{chave_menu} - {campo['nome']}")
        escolha_campo = input("Escolha uma opção (Enter para voltar): ").strip()
        if escolha_campo == "":
            continue
        if escolha_campo not in campos:
            print("Opção inválida!\n")
            continue

        ordenar_catalogo(algoritmo, campos[escolha_campo], filmes)


TAMANHO_PADRAO_COMPARATIVO = 1000


def ler_tamanho_amostra(total):
    while True:
        entrada = input(f"Quantos filmes usar? (1 a {total}, Enter = "
                        f"{TAMANHO_PADRAO_COMPARATIVO}): ").strip()
        if entrada == "":
            return min(TAMANHO_PADRAO_COMPARATIVO, total)
        if entrada.isdigit() and 1 <= int(entrada) <= total:
            return int(entrada)
        print("Valor inválido.\n")


def comparar_ordenacoes(filmes):
    campo = CAMPOS["1"]  # código: numérico, então todos os algoritmos se aplicam
    chave = campo["chave"]

    print("\n--- Comparativo de desempenho dos algoritmos de ordenação ---")
    print("(os algoritmos O(n^2) ficam lentos com o catálogo inteiro)")
    n = ler_tamanho_amostra(len(filmes))

    amostra = filmes[:n]
    crescente, _, _ = heap_sort(amostra, chave=chave)
    cenarios = {
        "Ordem original do CSV": amostra,
        "Já ordenado": crescente,
        "Ordem inversa": crescente[::-1],
    }

    for nome_cenario, entrada in cenarios.items():
        print(f"\n>> Cenário: {nome_cenario} | {n} filmes | chave: {campo['nome']}")
        cabecalho = f"{'Algoritmo':<18}{'Comparações':>14}{'Movimentações':>16}{'Tempo (ms)':>14}"
        print(cabecalho)
        print("-" * len(cabecalho))
        for algoritmo in ALGORITMOS_ORDENACAO.values():
            inicio = time.perf_counter()
            _, comparacoes, movimentacoes = algoritmo["funcao"](entrada, chave=chave)
            fim = time.perf_counter()
            print(f"{algoritmo['nome']:<18}{comparacoes:>14}{movimentacoes:>16}"
                  f"{(fim - inicio) * 1000:>14.4f}")
    print()


def menu_principal():
    filmes = carregar_filmes()
    estruturas = montar_estruturas(filmes)

    while True:
        print("=================================================")
        print("   CATÁLOGO DE FILMES - BUSCA E ORDENAÇÃO        ")
        print("=================================================")
        for chave_menu, nome in METODOS.items():
            print(f"{chave_menu} - {nome}")
        print("6 - Listar catálogo")
        print("7 - Comparar desempenho dos métodos")
        print("8 - Ordenar catálogo")
        print("9 - Comparar desempenho dos algoritmos de ordenação")
        print("0 - Sair")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando...")
            break
        elif escolha == "6":
            listar_catalogo(filmes)
        elif escolha == "7":
            comparar_metodos(filmes, estruturas)
        elif escolha == "8":
            menu_ordenacao(filmes)
        elif escolha == "9":
            comparar_ordenacoes(filmes)
        elif escolha in METODOS:
            menu_campo(escolha, METODOS[escolha], filmes, estruturas)
        else:
            print("Opção inválida!\n")


if __name__ == "__main__":
    menu_principal()
