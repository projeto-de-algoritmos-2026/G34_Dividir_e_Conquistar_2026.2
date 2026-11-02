import math
import sys

from ordenacoes import heap_sort, merge_sort

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def contar_inversoes(sequencia):
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
    return [(sequencia[i], sequencia[j])
            for i in range(len(sequencia))
            for j in range(i + 1, len(sequencia))
            if sequencia[i] > sequencia[j]]


def selecionar(valores, k, chave=lambda x: x, contador=None):
    if contador is None:
        contador = {"comparacoes": 0}
    if not 0 <= k < len(valores):
        raise IndexError("k fora do intervalo")
    return _selecionar(list(valores), k, chave, contador)


def _selecionar(v, k, chave, contador):
    if len(v) <= 5:
        return _ordenar_pequeno(v, chave, contador)[k]

    medianas = []
    for i in range(0, len(v), 5):
        grupo = _ordenar_pequeno(v[i:i + 5], chave, contador)
        medianas.append(grupo[len(grupo) // 2])

    pivo = _selecionar(medianas, len(medianas) // 2, chave, contador)
    chave_pivo = chave(pivo)

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

    if k < len(menores):
        return _selecionar(menores, k, chave, contador)
    if k < len(menores) + len(iguais):
        return pivo
    return _selecionar(maiores, k - len(menores) - len(iguais), chave, contador)


def _ordenar_pequeno(v, chave, contador):
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
    n = len(valores)
    if n == 0:
        raise ValueError("lista vazia")
    if n % 2 == 1:
        return selecionar(valores, n // 2, contador=contador)
    a = selecionar(valores, n // 2 - 1, contador=contador)
    b = selecionar(valores, n // 2, contador=contador)
    return (a + b) / 2


def percentil(valores, p, chave=lambda x: x, contador=None):
    k = min(len(valores) - 1, max(0, math.ceil(p / 100 * len(valores)) - 1))
    return selecionar(valores, k, chave=chave, contador=contador)


def mediana_ordenando(valores):
    ordenados, comparacoes, _ = heap_sort(valores, chave=lambda x: x)
    n = len(ordenados)
    if n % 2 == 1:
        return ordenados[n // 2], comparacoes
    return (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2, comparacoes


def distancia(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def par_mais_proximo(pontos):
    if len(pontos) < 2:
        raise ValueError("são necessários pelo menos 2 pontos")
    contador = {"calculos": 0}
    por_x, _, _ = merge_sort(pontos, chave=lambda p: p[0])
    d, p, q, _ = _par_recursivo(por_x, contador)
    return d, p, q, contador["calculos"]


def _par_recursivo(px, contador):
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

    meio = n // 2
    x_linha = px[meio][0]
    d1, p1, q1, y_esq = _par_recursivo(px[:meio], contador)
    d2, p2, q2, y_dir = _par_recursivo(px[meio:], contador)
    delta, p, q = (d1, p1, q1) if d1 <= d2 else (d2, p2, q2)

    por_y = _intercalar_por_y(y_esq, y_dir)

    faixa = [ponto for ponto in por_y if abs(ponto[0] - x_linha) < delta]

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


BITS_BASE = 32                    # "dígito" da máquina: 32 bits
LIMITE_BASE = 1 << BITS_BASE


def karatsuba(x, y, contador=None):
    if contador is None:
        contador = {"multiplicacoes": 0}

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
    if x == 0:
        return [0]
    bytes_x = x.to_bytes((x.bit_length() + 7) // 8, "little")
    return [int.from_bytes(bytes_x[i:i + 4], "little")
            for i in range(0, len(bytes_x), 4)]


def _de_digitos(digitos):
    return int.from_bytes(b"".join(d.to_bytes(4, "little") for d in digitos), "little")


def produto_intervalo(inicio, fim, multiplicar=karatsuba, contador=None):
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
    return produto_intervalo(n - k + 1, n, multiplicar, contador)


def combinacao(n, k, multiplicar=karatsuba, contador=None):
    k = min(k, n - k)
    return arranjo(n, k, multiplicar, contador) // produto_intervalo(1, k, multiplicar, contador)
