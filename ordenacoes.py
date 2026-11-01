def selection_sort(filmes, chave=lambda f: f.codigo):
    v = list(filmes)
    n = len(v)
    comparacoes = 0
    movimentacoes = 0

    for i in range(n - 1):
        indice_menor = i
        for j in range(i + 1, n):
            comparacoes += 1
            if chave(v[j]) < chave(v[indice_menor]):
                indice_menor = j
        if indice_menor != i:
            v[i], v[indice_menor] = v[indice_menor], v[i]
            movimentacoes += 2

    return v, comparacoes, movimentacoes


def insertion_sort(filmes, chave=lambda f: f.codigo):
    v = list(filmes)
    comparacoes = 0
    movimentacoes = 0

    for i in range(1, len(v)):
        atual = v[i]
        chave_atual = chave(atual)
        j = i - 1
        while j >= 0:
            comparacoes += 1
            if chave(v[j]) <= chave_atual:
                break
            v[j + 1] = v[j]          # desloca o maior uma posição pra direita
            movimentacoes += 1
            j -= 1
        if j + 1 != i:
            v[j + 1] = atual
            movimentacoes += 1

    return v, comparacoes, movimentacoes


def bubble_sort(filmes, chave=lambda f: f.codigo):
    v = list(filmes)
    comparacoes = 0
    movimentacoes = 0
    fim = len(v) - 1

    troca = True
    while troca:
        troca = False
        for i in range(fim):
            comparacoes += 1
            if chave(v[i]) > chave(v[i + 1]):
                v[i], v[i + 1] = v[i + 1], v[i]
                movimentacoes += 2
                troca = True
        fim -= 1

    return v, comparacoes, movimentacoes


def counting_sort(filmes, chave=lambda f: f.ano):
    v = list(filmes)
    n = len(v)
    if n <= 1:
        return v, 0, 0

    chaves = [chave(f) for f in v]
    minimo, maximo = min(chaves), max(chaves)
    k = maximo - minimo + 1

    c = [0] * k
    for x in chaves:                      # c[i] = qtd de elementos iguais a i
        c[x - minimo] += 1
    for i in range(1, k):                 # c[i] = qtd de elementos <= i
        c[i] += c[i - 1]

    b = [None] * n
    movimentacoes = 0
    for j in range(n - 1, -1, -1):        # de trás pra frente => estável
        posicao = chaves[j] - minimo
        c[posicao] -= 1
        b[c[posicao]] = v[j]
        movimentacoes += 1

    return b, 0, movimentacoes


def _counting_sort_por_digito(v, chave, divisor, base):
    c = [0] * base
    for filme in v:
        c[(chave(filme) // divisor) % base] += 1
    for i in range(1, base):
        c[i] += c[i - 1]

    b = [None] * len(v)
    for j in range(len(v) - 1, -1, -1):
        digito = (chave(v[j]) // divisor) % base
        c[digito] -= 1
        b[c[digito]] = v[j]
    return b


def radix_sort(filmes, chave=lambda f: f.codigo, base=10):
    v = list(filmes)
    if len(v) <= 1:
        return v, 0, 0

    maior = max(chave(f) for f in v)
    if min(chave(f) for f in v) < 0:
        raise ValueError("Radix sort só aceita chaves inteiras não negativas.")

    movimentacoes = 0
    divisor = 1
    while maior // divisor > 0:
        v = _counting_sort_por_digito(v, chave, divisor, base)
        movimentacoes += len(v)
        divisor *= base

    return v, 0, movimentacoes


def heap_sort(filmes, chave=lambda f: f.codigo):
    v = list(filmes)
    n = len(v)
    contador = {"comparacoes": 0, "movimentacoes": 0}

    def heapify(tamanho_heap, i):
        while True:
            esquerda = 2 * i + 1
            direita = 2 * i + 2
            maior = i

            if esquerda < tamanho_heap:
                contador["comparacoes"] += 1
                if chave(v[esquerda]) > chave(v[maior]):
                    maior = esquerda
            if direita < tamanho_heap:
                contador["comparacoes"] += 1
                if chave(v[direita]) > chave(v[maior]):
                    maior = direita

            if maior == i:
                return
            v[i], v[maior] = v[maior], v[i]
            contador["movimentacoes"] += 2
            i = maior

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    for fim in range(n - 1, 0, -1):
        v[0], v[fim] = v[fim], v[0]
        contador["movimentacoes"] += 2
        heapify(fim, 0)

    return v, contador["comparacoes"], contador["movimentacoes"]


def merge_sort(filmes, chave=lambda f: f.codigo):
    """Merge Sort: divide ao meio, ordena cada metade
    recursivamente e intercala. É a base da Contagem de Inversões (divisao_conquista.py)."""
    contador = {"comparacoes": 0, "movimentacoes": 0}

    def ordenar(v):
        if len(v) <= 1:
            return v
        meio = len(v) // 2
        esquerda = ordenar(v[:meio])
        direita = ordenar(v[meio:])

        resultado = []
        i = j = 0
        while i < len(esquerda) and j < len(direita):
            contador["comparacoes"] += 1
            if chave(esquerda[i]) <= chave(direita[j]):   # <= mantém estável
                resultado.append(esquerda[i])
                i += 1
            else:
                resultado.append(direita[j])
                j += 1
            contador["movimentacoes"] += 1
        resultado.extend(esquerda[i:])
        resultado.extend(direita[j:])
        contador["movimentacoes"] += (len(esquerda) - i) + (len(direita) - j)
        return resultado

    v = ordenar(list(filmes))
    return v, contador["comparacoes"], contador["movimentacoes"]
