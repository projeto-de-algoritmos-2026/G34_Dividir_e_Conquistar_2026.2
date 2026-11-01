def busca_sequencial(filmes, valor, chave=lambda f: f.codigo, chave_unica=False,
                      modo="igual", limite=None):
    comparacoes = 0
    encontrados = []
    for filme in filmes:
        comparacoes += 1
        chave_filme = chave(filme)
        bateu = chave_filme == valor if modo == "igual" else valor in chave_filme
        if bateu:
            encontrados.append(filme)
            if chave_unica or (limite is not None and len(encontrados) >= limite):
                break
    return encontrados, comparacoes


def _coletar_ocorrencias(filmes_ordenados, posicao, valor, chave, comparacoes):
    encontrados = [filmes_ordenados[posicao]]

    i = posicao - 1
    while i >= 0:
        comparacoes += 1
        if chave(filmes_ordenados[i]) != valor:
            break
        encontrados.append(filmes_ordenados[i])
        i -= 1

    i = posicao + 1
    while i < len(filmes_ordenados):
        comparacoes += 1
        if chave(filmes_ordenados[i]) != valor:
            break
        encontrados.append(filmes_ordenados[i])
        i += 1

    return encontrados, comparacoes


def busca_binaria(filmes_ordenados, valor, chave=lambda f: f.codigo):
    comparacoes = 0
    baixo, alto = 0, len(filmes_ordenados) - 1

    while baixo <= alto:
        meio = (baixo + alto) // 2
        comparacoes += 1
        chave_meio = chave(filmes_ordenados[meio])
        if chave_meio == valor:
            return _coletar_ocorrencias(filmes_ordenados, meio, valor, chave, comparacoes)
        elif chave_meio < valor:
            baixo = meio + 1
        else:
            alto = meio - 1

    return [], comparacoes


def busca_interpolacao(filmes_ordenados, valor, chave=lambda f: f.codigo):
    comparacoes = 0
    baixo, alto = 0, len(filmes_ordenados) - 1

    while (baixo <= alto and
           chave(filmes_ordenados[baixo]) <= valor <= chave(filmes_ordenados[alto])):
        comparacoes += 1

        chave_baixo = chave(filmes_ordenados[baixo])
        chave_alto = chave(filmes_ordenados[alto])

        if chave_alto == chave_baixo:
            if chave_baixo == valor:
                return _coletar_ocorrencias(filmes_ordenados, baixo, valor, chave, comparacoes)
            break

        # posição estimada (fórmula da interpolação linear)
        pos = baixo + ((valor - chave_baixo) * (alto - baixo)) // (chave_alto - chave_baixo)

        chave_pos = chave(filmes_ordenados[pos])
        if chave_pos == valor:
            return _coletar_ocorrencias(filmes_ordenados, pos, valor, chave, comparacoes)
        elif chave_pos < valor:
            baixo = pos + 1
        else:
            alto = pos - 1

    return [], comparacoes


class NoArvore:
    def __init__(self, filme):
        self.filmes = [filme]
        self.esquerda = None
        self.direita = None


class ArvoreBusca:
    def __init__(self, chave=lambda f: f.codigo):
        self.raiz = None
        self.chave = chave

    def inserir(self, filme):
        self.raiz = self._inserir(self.raiz, filme)

    def _inserir(self, no, filme):
        if no is None:
            return NoArvore(filme)

        chave_no = self.chave(no.filmes[0])
        chave_filme = self.chave(filme)

        if chave_filme < chave_no:
            no.esquerda = self._inserir(no.esquerda, filme)
        elif chave_filme > chave_no:
            no.direita = self._inserir(no.direita, filme)
        else:
            no.filmes.append(filme)
        return no

    def buscar(self, valor):
        comparacoes = 0
        no = self.raiz
        while no is not None:
            comparacoes += 1
            chave_no = self.chave(no.filmes[0])
            if valor == chave_no:
                return no.filmes, comparacoes
            elif valor < chave_no:
                no = no.esquerda
            else:
                no = no.direita
        return [], comparacoes

    def buscar_por_trecho(self, texto, limite=None):
        comparacoes = 0
        encontrados = []
        pilha = []
        no = self.raiz
        while no is not None or pilha:
            if limite is not None and len(encontrados) >= limite:
                break
            while no is not None:
                pilha.append(no)
                no = no.esquerda
            no = pilha.pop()
            for filme in no.filmes:
                comparacoes += 1
                if texto in self.chave(filme):
                    encontrados.append(filme)
                    if limite is not None and len(encontrados) >= limite:
                        break
            no = no.direita
        return encontrados, comparacoes


def montar_arvore_balanceada(filmes_ordenados, chave=lambda f: f.codigo):
    arvore = ArvoreBusca(chave=chave)

    def inserir_intervalo(baixo, alto):
        if baixo > alto:
            return
        meio = (baixo + alto) // 2
        arvore.inserir(filmes_ordenados[meio])
        inserir_intervalo(baixo, meio - 1)
        inserir_intervalo(meio + 1, alto)

    inserir_intervalo(0, len(filmes_ordenados) - 1)
    return arvore


def _eh_primo(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def tamanho_recomendado_para_hash(n_elementos, fator_carga_alvo=0.7):
    candidato = max(13, int(n_elementos / fator_carga_alvo))
    if candidato % 2 == 0:
        candidato += 1
    while not _eh_primo(candidato):
        candidato += 2
    return candidato


class TabelaHash:
    def __init__(self, tamanho=13, chave=lambda f: f.codigo):
        self.tamanho = tamanho
        self.chave = chave
        self.tabela = [[] for _ in range(tamanho)]

    def _hash(self, valor):
        if isinstance(valor, str):
            return sum(ord(c) for c in valor) % self.tamanho

        return valor % self.tamanho

    def inserir(self, filme):
        posicao = self._hash(self.chave(filme))
        self.tabela[posicao].append(filme)

    def buscar(self, valor):
        posicao = self._hash(valor)
        comparacoes = 0
        encontrados = []
        for filme in self.tabela[posicao]:
            comparacoes += 1
            if self.chave(filme) == valor:
                encontrados.append(filme)
        return encontrados, comparacoes

    def buscar_por_trecho(self, texto, limite=None):
        comparacoes = 0
        encontrados = []
        for bucket in self.tabela:
            for filme in bucket:
                comparacoes += 1
                if texto in self.chave(filme):
                    encontrados.append(filme)
                    if limite is not None and len(encontrados) >= limite:
                        return encontrados, comparacoes
        return encontrados, comparacoes
