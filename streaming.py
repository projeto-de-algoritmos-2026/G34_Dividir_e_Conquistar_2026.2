import random
import time

import ui
from buscas import busca_sequencial
from divisao_conquista import (
    contar_inversoes,
    contar_inversoes_forca_bruta,
    listar_pares_invertidos,
    mediana,
    mediana_ordenando,
    percentil,
    par_mais_proximo,
    par_mais_proximo_forca_bruta,
    karatsuba,
    multiplicacao_escolar,
    arranjo,
    combinacao,
)
from ordenacoes import bubble_sort
from usuarios import CODIGOS_RANKING, avaliacoes_da_comunidade


def escolher_filme(ctx):
    while True:
        entrada = ui.ler_texto("Código ou parte do título do filme (Enter = voltar)")
        if entrada == "":
            return None
        if entrada.isdigit():
            filme = ctx.por_codigo.get(int(entrada))
            if filme:
                return filme
            print("  >> Nenhum filme com esse código.")
            continue

        encontrados, _ = busca_sequencial(ctx.filmes, entrada.casefold(),
                                          chave=lambda f: f.titulo.casefold(),
                                          modo="contem", limite=10)
        if not encontrados:
            print("  >> Nenhum filme encontrado. Tente outro trecho (ex.: 'matrix').")
            continue
        if len(encontrados) == 1:
            return encontrados[0]
        for i, filme in enumerate(encontrados, 1):
            print(f"   {i:>2}) {filme.resumo()}")
        i = ui.ler_inteiro("Qual deles?", 1, len(encontrados))
        if i is not None:
            return encontrados[i - 1]


def histograma(notas):
    contagem = [0] * 11
    for n in notas:
        contagem[n] += 1
    maior = max(contagem)
    for nota in range(11):
        print(f"   {nota:>2} | {ui.barra(contagem[nota], maior, 36):<36} {contagem[nota]}")


def numero_grande(n):
    texto = str(n)
    if len(texto) <= 30:
        return ui.numero(n)
    return f"{texto[:15]}...{texto[-8:]}"


RANKING_EXEMPLO = [5, 1, 10, 8, 9, 2, 4, 7, 3, 6]


def menu_recomendacao(ctx):
    while True:
        escolha = ui.menu("RECOMENDAÇÃO POR GOSTO", [
            ("1", "Montar meu ranking e receber recomendações"),
            ("2", "Comparar o ranking de dois usuários"),
            ("3", "Desempenho: divisão e conquista x força bruta"),
        ], subtitulo="Algoritmo: Contagem de Inversões")
        if escolha == "0":
            return
        if escolha == "1":
            montar_meu_ranking(ctx)
        elif escolha == "2":
            comparar_dois_usuarios(ctx)
        elif escolha == "3":
            desempenho_inversoes()
        ui.pausar()


def _ler_ranking(n):
    print(f"\n  Digite os números dos {n} filmes do MAIS para o MENOS favorito,")
    print("  separados por espaço. Ex.: 5 1 10 8 9 2 4 7 3 6")
    while True:
        entrada = ui.ler_texto("Seu ranking (Enter = usar o exemplo acima)")
        if entrada == "":
            return RANKING_EXEMPLO[:n]
        partes = entrada.replace(",", " ").split()
        if all(p.isdigit() for p in partes) and sorted(map(int, partes)) == list(range(1, n + 1)):
            return [int(p) for p in partes]
        print(f"  >> Use cada número de 1 a {n} exatamente uma vez.")


def montar_meu_ranking(ctx):
    filmes = ctx.filmes_ranking
    n = len(filmes)
    ui.secao("Filmes para ranquear")
    for i, filme in enumerate(filmes, 1):
        print(f"   {i:>2}) {filme.titulo} ({filme.ano}) - {filme.genero}")

    escolha = _ler_ranking(n)
    meu_ranking = [filmes[i - 1].codigo for i in escolha]
    posicao = {codigo: i for i, codigo in enumerate(meu_ranking)}

    ui.secao("Seu ranking")
    for i, codigo in enumerate(meu_ranking, 1):
        print(f"   {i:>2}º {ctx.por_codigo[codigo].titulo}")

    inicio = time.perf_counter()
    resultados = []
    for usuario in ctx.usuarios:
        sequencia = [posicao[c] for c in usuario.ranking(meu_ranking)]
        _, inversoes = contar_inversoes(sequencia)
        resultados.append((inversoes, usuario.codigo, usuario))
    resultados.sort(key=lambda r: (r[0], r[1]))
    tempo = time.perf_counter() - inicio

    maximo = n * (n - 1) // 2
    ui.secao(f"Usuários com gosto mais parecido (de {len(ctx.usuarios)})")
    linhas = []
    for inversoes, _, usuario in resultados[:5]:
        favorito = ctx.por_codigo[usuario.ranking(meu_ranking)[0]].titulo
        similaridade = 100 * (1 - inversoes / maximo)
        linhas.append([str(usuario), inversoes, f"{similaridade:.0f}%", favorito[:22]])
    ui.tabela(["Usuário", "Inversões", "Parecido", "Favorito dele"], linhas, [-20, 9, 8, -22])
    print(f"\n  0 inversões = gosto idêntico | {maximo} = gosto totalmente oposto")
    print(f"  {len(ctx.usuarios)} comparações feitas em {ui.ms(tempo)}")

    vizinhos = [r[2] for r in resultados[:10]]
    indicados = {}
    for usuario in vizinhos:
        for codigo, nota in usuario.avaliacoes.items():
            if codigo not in posicao and nota >= 7.5:
                indicados.setdefault(codigo, []).append(nota)
    melhores = sorted(indicados.items(),
                      key=lambda item: (-len(item[1]), -sum(item[1]) / len(item[1])))[:5]

    ui.secao("Recomendados para você")
    linhas = [[ctx.por_codigo[c].titulo[:32], f"{len(notas)} de {len(vizinhos)}",
               f"{sum(notas) / len(notas):.1f}"] for c, notas in melhores]
    ui.tabela(["Filme", "Indicado por", "Nota deles"], linhas, [-32, 12, 10])


def comparar_dois_usuarios(ctx):
    total = len(ctx.usuarios)
    a = ui.ler_inteiro(f"Número do 1º usuário (1 a {total})", 1, total, padrao=1)
    b = ui.ler_inteiro(f"Número do 2º usuário (1 a {total})", 1, total, padrao=2)
    usuario_a, usuario_b = ctx.usuarios[a - 1], ctx.usuarios[b - 1]

    codigos = [f.codigo for f in ctx.filmes_ranking]
    ranking_a = usuario_a.ranking(codigos)
    ranking_b = usuario_b.ranking(codigos)
    posicao_a = {c: i + 1 for i, c in enumerate(ranking_a)}
    sequencia = [posicao_a[c] for c in ranking_b]

    ui.secao("Rankings lado a lado")
    linhas = [[f"{i}º", ctx.por_codigo[ca].titulo[:24], ctx.por_codigo[cb].titulo[:24], sequencia[i - 1]]
              for i, (ca, cb) in enumerate(zip(ranking_a, ranking_b), 1)]
    ui.tabela(["", str(usuario_a)[:24], str(usuario_b)[:24], "Pos. em A"], linhas, [-4, -24, -24, 9])

    _, inversoes = contar_inversoes(sequencia)
    print(f"\n  Sequência analisada: {sequencia}")
    print(f"  Inversões (divisão e conquista): {inversoes}")
    print(f"  Inversões (força bruta):         {contar_inversoes_forca_bruta(sequencia)}")

    pares = listar_pares_invertidos(sequencia)
    if pares:
        ui.secao("Onde eles discordam (pares invertidos)")
        for maior, menor in pares[:10]:
            fa = ctx.por_codigo[ranking_a[menor - 1]].titulo
            fb = ctx.por_codigo[ranking_a[maior - 1]].titulo
            print(f"   - A prefere '{fa}', B prefere '{fb}'")
        if len(pares) > 10:
            print(f"   ... e mais {len(pares) - 10} pares.")


def desempenho_inversoes():
    ui.secao("Contagem de Inversões: O(n log n) x força bruta O(n²)")
    rng = random.Random(42)
    linhas = []
    for n in (500, 1000, 2000, 4000):
        seq = rng.sample(range(n * 10), n)
        t0 = time.perf_counter()
        _, inv_dc = contar_inversoes(seq)
        t1 = time.perf_counter()
        inv_fb = contar_inversoes_forca_bruta(seq)
        t2 = time.perf_counter()
        linhas.append([ui.numero(n), ui.ms(t1 - t0), ui.ms(t2 - t1), ui.numero(inv_dc),
                       "sim" if inv_dc == inv_fb else "NÃO"])
    ui.tabela(["n", "Div. e Conq.", "Força bruta", "Inversões", "Confere"],
              linhas, [6, 13, 13, 11, 8])

    seq = rng.sample(range(10000), 1000)
    _, _, movimentacoes = bubble_sort(seq, chave=lambda x: x)
    print("\n  Curiosidade (Trabalho 2): trocas do Bubble Sort = inversões")
    print(f"  n = 1000 -> trocas do Bubble Sort: {ui.numero(movimentacoes // 2)}"
          f" | inversões: {ui.numero(contar_inversoes(seq)[1])}")


def menu_mapa(ctx):
    while True:
        escolha = ui.menu("MAPA DE GOSTOS", [
            ("1", "Par de usuários com gosto mais parecido"),
            ("2", "Par de filmes mais parecidos (nota x popularidade)"),
            ("3", "Desempenho: divisão e conquista x força bruta"),
        ], subtitulo="Algoritmo: Par de Pontos Mais Próximos")
        if escolha == "0":
            return
        if escolha == "1":
            par_de_usuarios(ctx)
        elif escolha == "2":
            par_de_filmes(ctx)
        elif escolha == "3":
            desempenho_par()
        ui.pausar()


def desenhar_mapa(pontos, p, q, rotulo_x, rotulo_y, largura=50, altura=16):
    xs = [pt[0] for pt in pontos]
    ys = [pt[1] for pt in pontos]
    x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)

    def celula(pt):
        c = int((pt[0] - x_min) / ((x_max - x_min) or 1) * (largura - 1))
        l = int((pt[1] - y_min) / ((y_max - y_min) or 1) * (altura - 1))
        return altura - 1 - l, c

    grade = [[" "] * largura for _ in range(altura)]
    for pt in pontos:
        l, c = celula(pt)
        grade[l][c] = "."
    lp, cp = celula(p)
    lq, cq = celula(q)
    grade[lp][cp] = "A"
    grade[lq][cq] = "B" if (lq, cq) != (lp, cp) else "@"

    print(f"\n   {rotulo_y}")
    for l, linha_grade in enumerate(grade):
        marca = f"{y_max:5.0f}" if l == 0 else (f"{y_min:5.0f}" if l == altura - 1 else "     ")
        print(f"  {marca} |{''.join(linha_grade)}")
    print("        +" + "-" * largura)
    print(f"        {x_min:<10.0f}{rotulo_x:^30}{x_max:>10.0f}")
    print("   A e B = par mais próximo  (@ = os dois no mesmo ponto do desenho)")


def par_de_usuarios(ctx):
    pontos = ctx.pontos_usuarios
    t0 = time.perf_counter()
    d, p, q, calculos = par_mais_proximo(pontos)
    tempo = time.perf_counter() - t0
    usuario_a, usuario_b = p[2], q[2]

    ui.secao(f"Mapa de gostos de {len(pontos)} usuários")
    desenhar_mapa(pontos, p, q, "gosta de Ação/Aventura ->", "^ gosta de Drama/Romance")

    ui.secao("Almas gêmeas encontradas")
    for rotulo, pt in (("A", p), ("B", q)):
        print(f"   {rotulo}: {str(pt[2]):<22} Ação {pt[0]:5.1f} | Drama {pt[1]:5.1f}")
    print(f"   Distância entre eles: {d:.3f}")
    n = len(pontos)
    print(f"   Distâncias calculadas: {ui.numero(calculos)} "
          f"(a força bruta calcularia {ui.numero(n * (n - 1) // 2)}) em {ui.ms(tempo)}")

    amaram = [c for c in usuario_a.avaliacoes
              if c in usuario_b.avaliacoes and min(usuario_a.avaliacoes[c], usuario_b.avaliacoes[c]) >= 8]
    if amaram:
        print("\n   Filmes que os dois amaram (nota >= 8):")
        for c in amaram[:5]:
            print(f"    - {ctx.por_codigo[c].titulo}")
    sugestoes = sorted((c for c in usuario_a.avaliacoes
                        if c not in usuario_b.avaliacoes and usuario_a.avaliacoes[c] >= 8),
                       key=lambda c: -usuario_a.avaliacoes[c])
    if sugestoes:
        print(f"\n   Sugestão para {usuario_b.nome}: assistir "
              f"'{ctx.por_codigo[sugestoes[0]].titulo}' (o par deu {usuario_a.avaliacoes[sugestoes[0]]})")


def par_de_filmes(ctx):
    genero = ui.ler_texto("Filtrar por gênero, ex.: Horror (Enter = todos)")
    filmes = [f for f in ctx.filmes if f.votos >= 100 and genero.casefold() in f.genero.casefold()]
    if len(filmes) < 2:
        print("  >> Poucos filmes com esse gênero.")
        return
    pontos = [(f.nota, f.popularidade, f) for f in filmes]
    t0 = time.perf_counter()
    d, p, q, calculos = par_mais_proximo(pontos)
    tempo = time.perf_counter() - t0

    ui.secao(f"{len(pontos)} filmes no mapa (com 100+ votos)")
    desenhar_mapa(pontos, p, q, "nota média ->", "^ popularidade")
    ui.secao("Filmes mais parecidos")
    for rotulo, pt in (("A", p), ("B", q)):
        print(f"   {rotulo}: {pt[2].titulo[:34]:<34} nota {pt[0]:.1f} | popularidade {pt[1]:.2f}")
    print(f"   Distância: {d:.4f} | distâncias calculadas: {ui.numero(calculos)} em {ui.ms(tempo)}")


def desempenho_par():
    ui.secao("Par Mais Próximo: O(n log n) x força bruta O(n²)")
    rng = random.Random(42)
    linhas = []
    for n in (500, 1000, 2000, 4000):
        pontos = [(rng.uniform(0, 100), rng.uniform(0, 100), i) for i in range(n)]
        t0 = time.perf_counter()
        d1, _, _, calc_dc = par_mais_proximo(pontos)
        t1 = time.perf_counter()
        d2, _, _, calc_fb = par_mais_proximo_forca_bruta(pontos)
        t2 = time.perf_counter()
        linhas.append([ui.numero(n), ui.ms(t1 - t0), ui.ms(t2 - t1), ui.numero(calc_dc),
                       ui.numero(calc_fb), "sim" if abs(d1 - d2) < 1e-12 else "NÃO"])
    ui.tabela(["n", "Div. e Conq.", "Força bruta", "Cálculos D&C", "Cálculos FB", "Confere"],
              linhas, [6, 13, 13, 13, 12, 8])
    print("\n  A faixa central só compara cada ponto com os 7 seguintes (ordenados por y).")


def menu_nota_robusta(ctx):
    while True:
        escolha = ui.menu("NOTA ROBUSTA", [
            ("1", "Nota de um filme (média x mediana)"),
            ("2", "Simular ataque de review bombing"),
            ("3", "Estatísticas do catálogo (mediana e percentis)"),
            ("4", "Desempenho: mediana das medianas x ordenação"),
        ], subtitulo="Algoritmo: Mediana das Medianas")
        if escolha == "0":
            return
        if escolha == "1":
            nota_de_um_filme(ctx)
        elif escolha == "2":
            review_bombing(ctx)
        elif escolha == "3":
            estatisticas_catalogo(ctx)
        elif escolha == "4":
            desempenho_mediana()
        ui.pausar()


def nota_de_um_filme(ctx):
    filme = escolher_filme(ctx)
    if not filme:
        return
    notas = avaliacoes_da_comunidade(filme)
    contador = {"comparacoes": 0}
    med = mediana(notas, contador=contador)

    ui.secao(filme.resumo())
    print(f"   Nota oficial do TMDB:   {filme.nota:.1f}")
    print(f"   Avaliações simuladas:   {ui.numero(len(notas))}")
    print(f"   Média das avaliações:   {sum(notas) / len(notas):.2f}")
    print(f"   Mediana (D&C, O(n)):    {med:.1f}   ({ui.numero(contador['comparacoes'])} comparações)")
    print("\n   Distribuição das notas:")
    histograma(notas)


def review_bombing(ctx):
    print("\n  Review bombing: um grupo combina de dar nota 0 em massa para")
    print("  derrubar a nota de um filme. Escolha a vítima:")
    filme = escolher_filme(ctx)
    if not filme:
        return
    notas = avaliacoes_da_comunidade(filme)
    sugestao = len(notas) * 4 // 10
    quantidade = ui.ler_inteiro("Quantas notas 0 o ataque vai injetar?", 1, 10 ** 6, padrao=sugestao)
    atacadas = notas + [0] * quantidade

    media_antes, media_depois = sum(notas) / len(notas), sum(atacadas) / len(atacadas)
    med_antes, med_depois = mediana(notas), mediana(atacadas)

    ui.secao(f"Ataque contra {filme.titulo}")
    ui.tabela(["Situação", "Avaliações", "Média", "Mediana"], [
        ["Antes do ataque", ui.numero(len(notas)), f"{media_antes:.2f}", f"{med_antes:.1f}"],
        ["Depois do ataque", ui.numero(len(atacadas)), f"{media_depois:.2f}", f"{med_depois:.1f}"],
    ], [-18, 11, 7, 8])
    print(f"\n   A média caiu   {media_antes - media_depois:.2f} pontos")
    print(f"   A mediana caiu {med_antes - med_depois:.2f} pontos")
    print("\n   A mediana só olha para o elemento do MEIO: as notas 0 empurram")
    print("   o meio só um pouco. Ela só desaba se o ataque for maior que todas")
    print("   as avaliações honestas juntas.")
    print("\n   Distribuição depois do ataque:")
    histograma(atacadas)


ESTATISTICAS = {
    "1": ("Duração (min)", lambda f: f.duracao, lambda v: f"{v} min"),
    "2": ("Orçamento (US$)", lambda f: f.orcamento, lambda v: "US$ " + ui.numero(v)),
    "3": ("Popularidade", lambda f: f.popularidade, lambda v: f"{v:.2f}"),
    "4": ("Nota média", lambda f: f.nota, lambda v: f"{v:.1f}"),
}


def estatisticas_catalogo(ctx):
    ui.secao("Qual campo analisar?")
    for k, (nome, _, _) in ESTATISTICAS.items():
        print(f"   {k} - {nome}")
    escolha = ui.ler_texto("Campo (Enter = voltar)")
    if escolha not in ESTATISTICAS:
        return
    nome, chave, formatar = ESTATISTICAS[escolha]
    filmes = [f for f in ctx.filmes if chave(f) > 0 and f.votos >= 10]

    contador = {"comparacoes": 0}
    t0 = time.perf_counter()
    linhas = []
    for rotulo, p in (("Mínimo", 0), ("Percentil 10", 10), ("Percentil 25", 25), ("MEDIANA", 50),
                      ("Percentil 75", 75), ("Percentil 90", 90), ("Máximo", 100)):
        filme = percentil(filmes, p, chave=chave, contador=contador)
        linhas.append([rotulo, formatar(chave(filme)), filme.titulo[:30]])
    tempo = time.perf_counter() - t0

    ui.secao(f"{nome} - {ui.numero(len(filmes))} filmes")
    ui.tabela(["Posição", "Valor", "Filme"], linhas, [-13, 20, -30])
    print(f"\n   7 seleções em O(n) cada, sem ordenar o catálogo: "
          f"{ui.numero(contador['comparacoes'])} comparações em {ui.ms(tempo)}")


def desempenho_mediana():
    ui.secao("Mediana: Mediana das Medianas O(n) x Heap Sort O(n log n)")
    rng = random.Random(42)
    linhas = []
    for n in (10_000, 50_000, 100_000, 200_000):
        valores = [rng.random() for _ in range(n)]
        contador = {"comparacoes": 0}
        t0 = time.perf_counter()
        m1 = mediana(valores, contador=contador)
        t1 = time.perf_counter()
        m2, comparacoes_heap = mediana_ordenando(valores)
        t2 = time.perf_counter()
        linhas.append([ui.numero(n), ui.ms(t1 - t0), ui.numero(contador["comparacoes"]),
                       ui.ms(t2 - t1), ui.numero(comparacoes_heap), "sim" if m1 == m2 else "NÃO"])
    ui.tabela(["n", "Med. medianas", "Comparações", "Heap Sort", "Comparações", "Confere"],
              linhas, [8, 14, 12, 13, 12, 8])
    print("\n  O Heap Sort é o do Trabalho 2: ordena tudo só para pegar o elemento do meio.")


def menu_maratona(ctx):
    while True:
        escolha = ui.menu("PLANEJADOR DE MARATONA", [
            ("1", "Quantas maratonas eu consigo montar?"),
            ("2", "Desempenho: Karatsuba x multiplicação escolar"),
        ], subtitulo="Algoritmo: Karatsuba")
        if escolha == "0":
            return
        if escolha == "1":
            planejar_maratona(ctx)
        elif escolha == "2":
            desempenho_karatsuba()
        ui.pausar()


def planejar_maratona(ctx):
    genero = ui.ler_texto("Filtrar por gênero, ex.: Horror (Enter = catálogo inteiro)")
    candidatos, _ = busca_sequencial(ctx.filmes, genero.casefold(),
                                     chave=lambda f: f.genero.casefold(), modo="contem")
    n = len(candidatos)
    if n == 0:
        print("  >> Nenhum filme com esse gênero.")
        return
    print(f"  -> {ui.numero(n)} filmes candidatos")
    k = ui.ler_inteiro("Quantos filmes na maratona?", 1, n, padrao=min(10, n))

    cont_arranjo = {"multiplicacoes": 0}
    cont_comb = {"multiplicacoes": 0}
    t0 = time.perf_counter()
    total_ordem = arranjo(n, k, contador=cont_arranjo)
    total_listas = combinacao(n, k, contador=cont_comb)
    tempo = time.perf_counter() - t0

    ui.secao(f"Maratonas de {k} filmes escolhidos entre {ui.numero(n)}")
    print(f"   Em ORDEM, sem repetir (arranjo A(n,k)):")
    print(f"      {numero_grande(total_ordem)}   ({ui.numero(len(str(total_ordem)))} dígitos)")
    print(f"   Só a LISTA, sem ordem (combinação C(n,k)):")
    print(f"      {numero_grande(total_listas)}   ({ui.numero(len(str(total_listas)))} dígitos)")
    print(f"\n   Multiplicações Karatsuba (casos base): "
          f"{ui.numero(cont_arranjo['multiplicacoes'] + cont_comb['multiplicacoes'])}"
          f" | tempo: {ui.ms(tempo)}")

    anos = total_ordem // (60 * 60 * 24 * 365)
    if anos > 0:
        digitos = str(anos)
        texto = ui.numero(anos) if anos < 10 ** 12 else f"cerca de {digitos[0]},{digitos[1]} x 10^{len(digitos) - 1}"
        print(f"   Assistindo UMA maratona por segundo, levaria {texto} anos.")
    if k == n:
        print("   (escolhendo TODOS os filmes só existe 1 lista; a combinação é máxima com k = metade)")

    exemplo = random.sample(candidatos, min(k, 5))
    print("\n   Exemplo de uma dessas maratonas:")
    for i, filme in enumerate(exemplo, 1):
        print(f"    {i}. {filme.resumo()}")
    if k > 5:
        print(f"    ... e mais {k - 5} filme(s)")

    if len(str(total_ordem)) > 30 and ui.confirmar("\n  Mostrar o número completo do arranjo?"):
        print(f"\n{total_ordem}")


def desempenho_karatsuba():
    ui.secao("Karatsuba O(n^1.585) x multiplicação escolar O(n²)")
    print("  (aguarde: a multiplicação escolar demora alguns segundos)\n")
    rng = random.Random(42)
    linhas = []
    for digitos in (1000, 5000, 10000, 20000, 30000):
        x = rng.randrange(10 ** (digitos - 1), 10 ** digitos)
        y = rng.randrange(10 ** (digitos - 1), 10 ** digitos)
        ck, ce = {"multiplicacoes": 0}, {"multiplicacoes": 0}
        t0 = time.perf_counter()
        rk = karatsuba(x, y, ck)
        t1 = time.perf_counter()
        re = multiplicacao_escolar(x, y, ce)
        t2 = time.perf_counter()
        ganho = (t2 - t1) / (t1 - t0) if t1 > t0 else 0
        linhas.append([ui.numero(digitos), ui.ms(t2 - t1), ui.ms(t1 - t0), ui.numero(ce["multiplicacoes"]),
                       ui.numero(ck["multiplicacoes"]), f"{ganho:.1f}x",
                       "sim" if rk == re == x * y else "NÃO"])
    ui.tabela(["Dígitos", "Escolar", "Karatsuba", "Mult. escolar", "Mult. Karat.", "Ganho", "Confere"],
              linhas, [8, 12, 12, 14, 13, 7, 8])
    print("  (Mult. = multiplicações de 'dígitos' de 32 bits)")

    ui.secao("Cenário real: maratona com o catálogo inteiro (4803!)")
    t0 = time.perf_counter()
    rk = arranjo(4803, 4803)
    t1 = time.perf_counter()
    re = arranjo(4803, 4803, multiplicar=multiplicacao_escolar)
    t2 = time.perf_counter()
    print(f"   Resultado com {ui.numero(len(str(rk)))} dígitos | iguais: {'sim' if rk == re else 'NÃO'}")
    print(f"   Escolar: {ui.ms(t2 - t1)} | Karatsuba: {ui.ms(t1 - t0)}")
