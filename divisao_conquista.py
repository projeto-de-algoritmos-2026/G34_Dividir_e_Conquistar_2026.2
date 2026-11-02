"""
Algoritmos de Divisão e Conquista (Trabalho 3).

Cada algoritmo tem a versão "dividir e conquistar" e uma versão de
FORÇA BRUTA, usada para validar o resultado e comparar o desempenho.

  1. Contagem de Inversões ........ O(n log n)   x  força bruta O(n²)
  2. Mediana das Medianas ......... O(n)         x  ordenar (Heap Sort) O(n log n)
  3. Par de Pontos Mais Próximos .. O(n log n)   x  força bruta O(n²)
  4. Karatsuba .................... O(n^1.585)   x  multiplicação escolar O(n²)
"""
import math
import sys

from ordenacoes import heap_sort, merge_sort

# Python >= 3.11 limita a conversão de inteiros gigantes para texto
# (4300 dígitos). Os números do planejador de maratona passam disso.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


# ======================================================================
# 1. CONTAGEM DE INVERSÕES (Sort-and-Count, Kleinberg & Tardos 5.3)
# ======================================================================
# Inversão: par (i, j) com i < j e a[i] > a[j].
# Mede o quanto uma sequência está "fora de ordem" -> distância entre
# dois rankings (filtragem colaborativa / recomendação).

def contar_inversoes(sequencia):
    """Retorna (lista_ordenada, numero_de_inversoes)."""
    if len(sequencia) <= 1:
        return list(sequencia), 0

    meio = len(sequencia) // 2
    esquerda, inv_esquerda = contar_inversoes(sequencia[:meio])     # dividir
    direita, inv_direita = contar_inversoes(sequencia[meio:])

    intercalada, inv_cruzadas = _merge_and_count(esquerda, direita)  # combinar
    return intercalada, inv_esquerda + inv_direita + inv_cruzadas


def _merge_and_count(a, b):
    resultado = []
    inversoes = 0
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            resultado.append(a[i])
            i += 1
        else:
            # b[j] é menor que TODOS os elementos restantes de a
            # -> forma uma inversão com cada um deles
            resultado.append(b[j])
            inversoes += len(a) - i
            j += 1
    resultado.extend(a[i:])
    resultado.extend(b[j:])
    return resultado, inversoes


def contar_inversoes_forca_bruta(sequencia):
    inversoes = 0
    n = len(sequencia)
    for i in range(n):
        for j in range(i + 1, n):
            if sequencia[i] > sequencia[j]:
                inversoes += 1
    return inversoes


def listar_pares_invertidos(sequencia):
    """Lista explicitamente os pares invertidos (só para exibição didática)."""
    return [(sequencia[i], sequencia[j])
            for i in range(len(sequencia))
            for j in range(i + 1, len(sequencia))
            if sequencia[i] > sequencia[j]]


# ======================================================================
# 2. MEDIANA DAS MEDIANAS (seleção em tempo linear - BFPRT)
# ======================================================================
# selecionar(v, k) devolve o k-ésimo menor elemento (k começa em 0)
# sem ordenar o vetor inteiro.

def selecionar(valores, k, chave=lambda x: x, contador=None):
    if contador is None:
        contador = {"comparacoes": 0}
    if not 0 <= k < len(valores):
        raise IndexError("k fora do intervalo")
    return _selecionar(list(valores), k, chave, contador)


def _selecionar(v, k, chave, contador):
    # caso base: poucos elementos -> ordena direto
    if len(v) <= 5:
        return _ordenar_pequeno(v, chave, contador)[k]

    # 1) divide em grupos de 5 e pega a mediana de cada grupo
    medianas = []
    for i in range(0, len(v), 5):
        grupo = _ordenar_pequeno(v[i:i + 5], chave, contador)
        medianas.append(grupo[len(grupo) // 2])

    # 2) acha RECURSIVAMENTE a mediana das medianas -> pivô
    pivo = _selecionar(medianas, len(medianas) // 2, chave, contador)
    chave_pivo = chave(pivo)

    # 3) particiona em menores / iguais / maiores
    #    (três partes porque notas e durações repetem muito)
    menores, iguais, maiores = [], [], []
    for x in v:
        contador["comparacoes"] += 1
        cx = chave(x)
        if cx < chave_pivo:
            menores.append(x)
        elif cx > chave_pivo:
            maiores.append(x)
        else:
            iguais.append(x)

    # 4) continua só do lado onde o k-ésimo está
    if k < len(menores):
        return _selecionar(menores, k, chave, contador)
    if k < len(menores) + len(iguais):
        return pivo
    return _selecionar(maiores, k - len(menores) - len(iguais), chave, contador)


def _ordenar_pequeno(v, chave, contador):
    """Insertion sort para grupos de até 5 elementos (custo constante)."""
    v = list(v)
    for i in range(1, len(v)):
        atual = v[i]
        j = i - 1
        while j >= 0:
            contador["comparacoes"] += 1
            if chave(v[j]) <= chave(atual):
                break
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = atual
    return v


def mediana(valores, contador=None):
    """Mediana numérica em O(n). Com n par, média dos dois do meio."""
    n = len(valores)
    if n == 0:
        raise ValueError("lista vazia")
    if n % 2 == 1:
        return selecionar(valores, n // 2, contador=contador)
    a = selecionar(valores, n // 2 - 1, contador=contador)
    b = selecionar(valores, n // 2, contador=contador)
    return (a + b) / 2


def percentil(valores, p, chave=lambda x: x, contador=None):
    """Elemento no percentil p (0 a 100), via seleção linear."""
    k = min(len(valores) - 1, max(0, math.ceil(p / 100 * len(valores)) - 1))
    return selecionar(valores, k, chave=chave, contador=contador)


def mediana_ordenando(valores):
    """Força bruta: ordena tudo com o Heap Sort do Trabalho 2 e pega o meio."""
    ordenados, comparacoes, _ = heap_sort(valores, chave=lambda x: x)
    n = len(ordenados)
    if n % 2 == 1:
        return ordenados[n // 2], comparacoes
    return (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2, comparacoes


# ======================================================================
# 3. PAR DE PONTOS MAIS PRÓXIMOS (Kleinberg & Tardos 5.4)
# ======================================================================
# Pontos são tuplas (x, y, rotulo). Retorna (distancia, p, q, calculos).

def distancia(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def par_mais_proximo(pontos):
    if len(pontos) < 2:
        raise ValueError("são necessários pelo menos 2 pontos")
    contador = {"calculos": 0}
    # ordena por x uma única vez (Merge Sort - também D&C)
    por_x, _, _ = merge_sort(pontos, chave=lambda p: p[0])
    d, p, q, _ = _par_recursivo(por_x, contador)
    return d, p, q, contador["calculos"]


def _par_recursivo(px, contador):
    """px: pontos ordenados por x.
    Devolve (dist, p, q, pontos_ordenados_por_y)."""
    n = len(px)
    if n <= 3:
        melhor = (math.inf, None, None)
        for i in range(n):
            for j in range(i + 1, n):
                contador["calculos"] += 1
                d = distancia(px[i], px[j])
                if d < melhor[0]:
                    melhor = (d, px[i], px[j])
        por_y = sorted(px, key=lambda p: p[1])
        return melhor[0], melhor[1], melhor[2], por_y

    # DIVIDIR: linha vertical L no meio
    meio = n // 2
    x_linha = px[meio][0]
    d1, p1, q1, y_esq = _par_recursivo(px[:meio], contador)
    d2, p2, q2, y_dir = _par_recursivo(px[meio:], contador)
    delta, p, q = (d1, p1, q1) if d1 <= d2 else (d2, p2, q2)

    # intercala as duas listas por y (como no merge sort) -> O(n)
    por_y = _intercalar_por_y(y_esq, y_dir)

    # COMBINAR: só pontos a menos de delta da linha L (a "faixa" 2δ)
    faixa = [ponto for ponto in por_y if abs(ponto[0] - x_linha) < delta]

    # cada ponto da faixa só precisa ser comparado com os 7 seguintes
    for i in range(len(faixa)):
        for j in range(i + 1, min(i + 8, len(faixa))):
            contador["calculos"] += 1
            d = distancia(faixa[i], faixa[j])
            if d < delta:
                delta, p, q = d, faixa[i], faixa[j]

    return delta, p, q, por_y


def _intercalar_por_y(a, b):
    resultado = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i][1] <= b[j][1]:
            resultado.append(a[i])
            i += 1
        else:
            resultado.append(b[j])
            j += 1
    resultado.extend(a[i:])
    resultado.extend(b[j:])
    return resultado


def par_mais_proximo_forca_bruta(pontos):
    melhor = (math.inf, None, None)
    calculos = 0
    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            calculos += 1
            d = distancia(pontos[i], pontos[j])
            if d < melhor[0]:
                melhor = (d, pontos[i], pontos[j])
    return melhor[0], melhor[1], melhor[2], calculos


# ======================================================================
# 4. KARATSUBA (multiplicação de inteiros grandes, K&T 5.5)
# ======================================================================
# Mesma ideia do slide, mas em base 2: dividir por 2^m é só deslocar
# bits, que é o que o computador faz de graça (no slide é base 10).
#   x = a·2^m + b      y = c·2^m + d
#   x·y = ac·2^(2m) + ((a+b)(c+d) - ac - bd)·2^m + bd
# -> 3 multiplicações de metade do tamanho em vez de 4.

BITS_BASE = 32                    # "dígito" da máquina: 32 bits
LIMITE_BASE = 1 << BITS_BASE


def karatsuba(x, y, contador=None):
    if contador is None:
        contador = {"multiplicacoes": 0}

    # caso base: cabe em um "dígito" de 32 bits -> multiplicação direta
    if x < LIMITE_BASE or y < LIMITE_BASE:
        contador["multiplicacoes"] += 1
        return x * y

    m = max(x.bit_length(), y.bit_length()) // 2
    mascara = (1 << m) - 1
    a, b = x >> m, x & mascara        # x = a·2^m + b
    c, d = y >> m, y & mascara        # y = c·2^m + d

    ac = karatsuba(a, c, contador)
    bd = karatsuba(b, d, contador)
    abcd = karatsuba(a + b, c + d, contador)

    return (ac << (2 * m)) + ((abcd - ac - bd) << m) + bd


def multiplicacao_escolar(x, y, contador=None):
    """Força bruta O(n²): o algoritmo "de papel" do slide, dígito a dígito,
    usando dígitos de 32 bits (mesma base do caso base do Karatsuba)."""
    if contador is None:
        contador = {"multiplicacoes": 0}
    a = _para_digitos(x)
    b = _para_digitos(y)
    resultado = [0] * (len(a) + len(b))
    mascara = LIMITE_BASE - 1

    for i, ai in enumerate(a):
        vai_um = 0
        for j, bj in enumerate(b):
            contador["multiplicacoes"] += 1
            t = resultado[i + j] + ai * bj + vai_um
            resultado[i + j] = t & mascara
            vai_um = t >> BITS_BASE
        resultado[i + len(b)] += vai_um

    return _de_digitos(resultado)


def _para_digitos(x):
    """Inteiro -> lista de dígitos de 32 bits (menos significativo primeiro)."""
    if x == 0:
        return [0]
    bytes_x = x.to_bytes((x.bit_length() + 7) // 8, "little")
    return [int.from_bytes(bytes_x[i:i + 4], "little")
            for i in range(0, len(bytes_x), 4)]


def _de_digitos(digitos):
    return int.from_bytes(b"".join(d.to_bytes(4, "little") for d in digitos), "little")


def produto_intervalo(inicio, fim, multiplicar=karatsuba, contador=None):
    """inicio × (inicio+1) × ... × fim, por divisão e conquista
    (árvore de produtos): os números multiplicados ficam do mesmo tamanho,
    que é o melhor caso para o Karatsuba."""
    if contador is None:
        contador = {"multiplicacoes": 0}
    if inicio > fim:
        return 1
    if inicio == fim:
        return inicio
    meio = (inicio + fim) // 2
    esquerda = produto_intervalo(inicio, meio, multiplicar, contador)
    direita = produto_intervalo(meio + 1, fim, multiplicar, contador)
    return multiplicar(esquerda, direita, contador)


def arranjo(n, k, multiplicar=karatsuba, contador=None):
    """A(n, k) = n! / (n-k)!  -> maratonas EM ORDEM, sem repetir filme."""
    return produto_intervalo(n - k + 1, n, multiplicar, contador)


def combinacao(n, k, multiplicar=karatsuba, contador=None):
    """C(n, k) = A(n, k) / k!  -> listas de filmes SEM ordem."""
    k = min(k, n - k)
    return arranjo(n, k, multiplicar, contador) // produto_intervalo(1, k, multiplicar, contador)
