import time

import ui
import streaming
from filmes import carregar_filmes
from usuarios import CODIGOS_RANKING, gerar_usuarios, exportar_usuarios_csv
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
    merge_sort,
)

# quantas ocorrências uma busca por trecho (título/gênero) devolve no
# máximo -- ela para de procurar assim que atingir esse número.
LIMITE_BUSCA_POR_TRECHO = 10
LIMITE_RESULTADOS_EXIBIDOS = 20
TAMANHO_PADRAO_COMPARATIVO = 1000

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
    "7": {"nome": "Merge Sort", "funcao": merge_sort, "apenas_numerico": False},
}


class Contexto:
    """Tudo que o programa carrega uma vez na inicialização."""

    def __init__(self):
        print("Carregando catálogo e gerando usuários simulados...")
        self.filmes = carregar_filmes()
        self.por_codigo = {f.codigo: f for f in self.filmes}
        self.estruturas = montar_estruturas(self.filmes)
        self.usuarios = gerar_usuarios(self.filmes)
        self.filmes_ranking = [self.por_codigo[c] for c in CODIGOS_RANKING if c in self.por_codigo]
        self.pontos_usuarios = [u.ponto_no_mapa(self.por_codigo) for u in self.usuarios]


# ======================================================================
# BUSCA (Trabalho 2)
# ======================================================================

def montar_estruturas(filmes):
    estruturas = {}
    tamanho_hash = tamanho_recomendado_para_hash(len(filmes))
    for campo in CAMPOS.values():
        chave = campo["chave"]
        # vetor ordenado usado pela busca binária / interpolação, gerado
        # pelo nosso Heap Sort (O(n log n)) em vez do sorted() do Python
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


def ler_valor_busca(campo):
    rotulo = campo["nome"] + (" (contém)" if campo["modo"] == "contem" else "")
    while True:
        entrada = input(f"  {rotulo} (Enter para voltar): ").strip()
        if entrada == "":
            return None
        try:
            return campo["conversor"](entrada)
        except ValueError:
            print("  >> Valor inválido para este campo.")


def buscar_no_submenu(metodo_id, metodo_nome, campo, ctx):
    ui.secao(f"{metodo_nome} | Campo: {campo['nome']}")
    while True:
        valor = ler_valor_busca(campo)
        if valor is None:
            return

        inicio = time.perf_counter()
        encontrados, comparacoes = executar_busca(metodo_id, campo, valor, ctx.filmes, ctx.estruturas)
        fim = time.perf_counter()

        if encontrados:
            print(f"  {len(encontrados)} filme(s) encontrado(s):")
            for filme in encontrados[:LIMITE_RESULTADOS_EXIBIDOS]:
                print("   ", filme)
            excedente = len(encontrados) - LIMITE_RESULTADOS_EXIBIDOS
            if excedente > 0:
                print(f"    ... e mais {excedente} filme(s) (não exibidos).")
        else:
            print("  Nenhum filme encontrado.")
        print(f"  Comparações: {comparacoes} | Tempo: {(fim - inicio) * 1000:.4f} ms\n")


def menu_busca(ctx):
    while True:
        escolha = ui.menu("BUSCAR FILMES", list(METODOS.items()),
                          subtitulo="Passo 1 de 2: escolha o método de busca")
        if escolha == "0":
            return
        metodo_nome = METODOS[escolha]
        opcoes = [(k, c["nome"]) for k, c in CAMPOS.items()]
        campo_id = ui.menu(metodo_nome.upper(), opcoes,
                           subtitulo="Passo 2 de 2: buscar por qual campo?")
        if campo_id != "0":
            buscar_no_submenu(escolha, metodo_nome, CAMPOS[campo_id], ctx)


def comparar_metodos_busca(ctx):
    campo = CAMPOS["1"]
    codigos_existentes = [f.codigo for f in ctx.filmes]
    codigo_inexistente = max(codigos_existentes) + 1

    ui.secao("Comparativo dos métodos de busca (busca por código)")
    print(f"  {len(codigos_existentes)} buscas bem-sucedidas (uma por filme do catálogo)\n")
    linhas = []
    for metodo_id, nome in METODOS.items():
        comparacoes_lista = []
        inicio = time.perf_counter()
        for codigo in codigos_existentes:
            _, comparacoes = executar_busca(metodo_id, campo, codigo, ctx.filmes, ctx.estruturas)
            comparacoes_lista.append(comparacoes)
        _, comparacoes_ausente = executar_busca(metodo_id, campo, codigo_inexistente,
                                                ctx.filmes, ctx.estruturas)
        fim = time.perf_counter()
        linhas.append([nome, min(comparacoes_lista), max(comparacoes_lista),
                       f"{sum(comparacoes_lista) / len(comparacoes_lista):.2f}",
                       comparacoes_ausente, f"{(fim - inicio) * 1000:.2f}"])
    ui.tabela(["Método", "Melhor", "Pior", "Médio", "Malsucedida", "Tempo (ms)"],
              linhas, [-24, 7, 7, 9, 12, 11])


# ======================================================================
# ORDENAÇÃO (Trabalho 2)
# ======================================================================

def ordenar_catalogo(algoritmo, campo, filmes):
    ui.secao(f"{algoritmo['nome']} | Campo: {campo['nome']}")
    inicio = time.perf_counter()
    ordenados, comparacoes, movimentacoes = algoritmo["funcao"](filmes, chave=campo["chave"])
    fim = time.perf_counter()

    print(f"  Primeiros {LIMITE_RESULTADOS_EXIBIDOS} de {len(ordenados)} filmes ordenados:")
    for filme in ordenados[:LIMITE_RESULTADOS_EXIBIDOS]:
        print("   ", filme)
    print(f"\n  Comparações: {ui.numero(comparacoes)} | Movimentações: {ui.numero(movimentacoes)} | "
          f"Tempo: {(fim - inicio) * 1000:.2f} ms")
    if algoritmo["funcao"] in (selection_sort, insertion_sort, bubble_sort):
        print("  (algoritmo O(n²): com o catálogo inteiro pode levar alguns segundos)")


def menu_ordenacao(ctx):
    while True:
        opcoes = [(k, a["nome"] + ("  (só código/ano)" if a["apenas_numerico"] else ""))
                  for k, a in ALGORITMOS_ORDENACAO.items()]
        escolha = ui.menu("ORDENAR CATÁLOGO", opcoes,
                          subtitulo="Passo 1 de 2: escolha o algoritmo")
        if escolha == "0":
            return
        algoritmo = ALGORITMOS_ORDENACAO[escolha]
        campos = {k: c for k, c in CAMPOS.items() if c["numerico"] or not algoritmo["apenas_numerico"]}
        campo_id = ui.menu(algoritmo["nome"].upper(), [(k, c["nome"]) for k, c in campos.items()],
                           subtitulo="Passo 2 de 2: ordenar por qual campo?")
        if campo_id == "0":
            continue
        ordenar_catalogo(algoritmo, campos[campo_id], ctx.filmes)
        ui.pausar()


def comparar_ordenacoes(ctx):
    campo = CAMPOS["1"]  # código: numérico, então todos os algoritmos se aplicam
    chave = campo["chave"]

    ui.secao("Comparativo dos algoritmos de ordenação")
    print("  (os algoritmos O(n²) ficam lentos com o catálogo inteiro)")
    n = ui.ler_inteiro(f"Quantos filmes usar? (1 a {len(ctx.filmes)})", 1, len(ctx.filmes),
                       padrao=min(TAMANHO_PADRAO_COMPARATIVO, len(ctx.filmes)))

    amostra = ctx.filmes[:n]
    crescente, _, _ = heap_sort(amostra, chave=chave)
    cenarios = {
        "Ordem original do CSV": amostra,
        "Já ordenado": crescente,
        "Ordem inversa": crescente[::-1],
    }

    for nome_cenario, entrada in cenarios.items():
        print(f"\n  >> Cenário: {nome_cenario} | {n} filmes | chave: {campo['nome']}")
        linhas = []
        for algoritmo in ALGORITMOS_ORDENACAO.values():
            inicio = time.perf_counter()
            _, comparacoes, movimentacoes = algoritmo["funcao"](entrada, chave=chave)
            fim = time.perf_counter()
            linhas.append([algoritmo["nome"], ui.numero(comparacoes), ui.numero(movimentacoes),
                           f"{(fim - inicio) * 1000:.2f}"])
        ui.tabela(["Algoritmo", "Comparações", "Movimentações", "Tempo (ms)"],
                  linhas, [-16, 13, 15, 12])


# ======================================================================
# COMPARATIVOS E DADOS
# ======================================================================

def menu_comparativos(ctx):
    acoes = {
        "1": lambda: comparar_metodos_busca(ctx),
        "2": lambda: comparar_ordenacoes(ctx),
        "3": streaming.desempenho_inversoes,
        "4": streaming.desempenho_par,
        "5": streaming.desempenho_mediana,
        "6": streaming.desempenho_karatsuba,
    }
    while True:
        escolha = ui.menu("COMPARATIVOS DE DESEMPENHO", [
            ("", "Trabalho 2:"),
            ("1", "Métodos de busca"),
            ("2", "Algoritmos de ordenação"),
            None,
            ("", "Divisão e conquista x força bruta:"),
            ("3", "Contagem de Inversões"),
            ("4", "Par de Pontos Mais Próximos"),
            ("5", "Mediana das Medianas"),
            ("6", "Karatsuba"),
        ])
        if escolha == "0":
            return
        acoes[escolha]()
        ui.pausar()


def menu_dados(ctx):
    while True:
        escolha = ui.menu("DADOS", [
            ("1", "Listar catálogo completo (ordenado por código)"),
            ("2", "Ver alguns usuários simulados"),
            ("3", "Exportar usuários simulados para usuarios.csv"),
        ])
        if escolha == "0":
            return
        if escolha == "1":
            ordenados, _, _ = merge_sort(ctx.filmes, chave=lambda f: f.codigo)
            for filme in ordenados:
                print("   ", filme)
        elif escolha == "2":
            linhas = []
            for u in ctx.usuarios[:10]:
                x, y, _ = u.ponto_no_mapa(ctx.por_codigo)
                favorito = max(u.avaliacoes, key=u.avaliacoes.get)
                linhas.append([str(u), len(u.avaliacoes), f"{x:.1f}", f"{y:.1f}",
                               ctx.por_codigo[favorito].titulo[:24]])
            ui.secao(f"Primeiros 10 de {len(ctx.usuarios)} usuários simulados")
            ui.tabela(["Usuário", "Avaliou", "Ação", "Drama", "Filme favorito"],
                      linhas, [-20, 8, 6, 6, -24])
        elif escolha == "3":
            caminho = exportar_usuarios_csv(ctx.usuarios, ctx.por_codigo)
            print(f"  Arquivo salvo em: {caminho}")
        ui.pausar()


# ======================================================================
# MENU PRINCIPAL
# ======================================================================

def menu_principal():
    ctx = Contexto()
    acoes = {
        "1": menu_busca,
        "2": menu_ordenacao,
        "3": streaming.menu_recomendacao,
        "4": streaming.menu_mapa,
        "5": streaming.menu_nota_robusta,
        "6": streaming.menu_maratona,
        "7": menu_comparativos,
        "8": menu_dados,
    }
    while True:
        escolha = ui.menu("CATÁLOGO DE FILMES", [
            ("", "Catálogo:"),
            ("1", "Buscar filmes"),
            ("2", "Ordenar catálogo"),
            None,
            ("", "Divisão e conquista:"),
            ("3", "Recomendação por gosto      [Contagem de Inversões]"),
            ("4", "Mapa de gostos              [Par de Pontos Mais Próximos]"),
            ("5", "Nota robusta                [Mediana das Medianas]"),
            ("6", "Planejador de maratona      [Karatsuba]"),
            None,
            ("7", "Comparativos de desempenho"),
            ("8", "Dados (catálogo e usuários)"),
        ], subtitulo=f"{ui.numero(len(ctx.filmes))} filmes | {ui.numero(len(ctx.usuarios))} usuários simulados",
            texto_sair="Sair")
        if escolha == "0":
            print("  Encerrando... até a próxima sessão!")
            return
        acoes[escolha](ctx)


if __name__ == "__main__":
    menu_principal()
