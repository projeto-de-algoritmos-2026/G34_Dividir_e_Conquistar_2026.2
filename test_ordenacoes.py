import random
import unittest

from filmes import Filme
from ordenacoes import (
    selection_sort,
    insertion_sort,
    bubble_sort,
    counting_sort,
    radix_sort,
    heap_sort,
    merge_sort,
)

ALGORITMOS = {
    "selection": selection_sort,
    "insertion": insertion_sort,
    "bubble": bubble_sort,
    "counting": counting_sort,
    "radix": radix_sort,
    "heap": heap_sort,
    "merge": merge_sort,
}

ESTAVEIS = {"insertion", "bubble", "counting", "radix", "merge"}


def gerar_filmes(n, semente=42):
    aleatorio = random.Random(semente)
    return [
        Filme(codigo=aleatorio.randint(0, 500000),
              titulo=f"Filme {i}",
              ano=aleatorio.randint(1916, 2017),
              genero="Drama")
        for i in range(n)
    ]


class TestOrdenacoes(unittest.TestCase):

    def verificar(self, nome, filmes, chave):
        algoritmo = ALGORITMOS[nome]
        esperado = sorted(filmes, key=chave)
        resultado, comparacoes, movimentacoes = algoritmo(filmes, chave=chave)
        self.assertEqual([chave(f) for f in resultado], [chave(f) for f in esperado],
                         f"{nome} ordenou errado")
        self.assertGreaterEqual(comparacoes, 0)
        self.assertGreaterEqual(movimentacoes, 0)
        return resultado

    def test_ordena_por_codigo(self):
        filmes = gerar_filmes(300)
        for nome in ALGORITMOS:
            with self.subTest(algoritmo=nome):
                self.verificar(nome, filmes, chave=lambda f: f.codigo)

    def test_ordena_por_ano_com_repeticoes(self):
        filmes = gerar_filmes(300)
        for nome in ALGORITMOS:
            with self.subTest(algoritmo=nome):
                self.verificar(nome, filmes, chave=lambda f: f.ano)

    def test_ordena_por_titulo_algoritmos_comparativos(self):
        filmes = gerar_filmes(100)
        random.Random(1).shuffle(filmes)
        for nome in ("selection", "insertion", "bubble", "heap", "merge"):
            with self.subTest(algoritmo=nome):
                self.verificar(nome, filmes, chave=lambda f: f.titulo.casefold())

    def test_casos_limite(self):
        for nome in ALGORITMOS:
            with self.subTest(algoritmo=nome):
                self.verificar(nome, [], chave=lambda f: f.codigo)
                self.verificar(nome, gerar_filmes(1), chave=lambda f: f.codigo)

    def test_nao_altera_lista_original(self):
        filmes = gerar_filmes(50)
        copia = list(filmes)
        for nome, algoritmo in ALGORITMOS.items():
            with self.subTest(algoritmo=nome):
                algoritmo(filmes, chave=lambda f: f.codigo)
                self.assertEqual(filmes, copia)

    def test_estabilidade(self):
        # mesmos anos, ordem original marcada pelo código
        filmes = [Filme(codigo=i, titulo=str(i), ano=2000 + (i % 3), genero="X")
                  for i in range(30)]
        for nome in ESTAVEIS:
            with self.subTest(algoritmo=nome):
                resultado = self.verificar(nome, filmes, chave=lambda f: f.ano)
                for a, b in zip(resultado, resultado[1:]):
                    if a.ano == b.ano:
                        self.assertLess(a.codigo, b.codigo, f"{nome} não foi estável")

    def test_insertion_e_bubble_lineares_em_vetor_ordenado(self):
        filmes = sorted(gerar_filmes(200), key=lambda f: f.codigo)
        for nome in ("insertion", "bubble"):
            with self.subTest(algoritmo=nome):
                _, comparacoes, movimentacoes = ALGORITMOS[nome](filmes, chave=lambda f: f.codigo)
                self.assertEqual(comparacoes, len(filmes) - 1)
                self.assertEqual(movimentacoes, 0)

    def test_radix_rejeita_negativos(self):
        filmes = [Filme(codigo=-5, titulo="x", ano=0, genero="x"),
                  Filme(codigo=3, titulo="y", ano=0, genero="y")]
        with self.assertRaises(ValueError):
            radix_sort(filmes, chave=lambda f: f.codigo)


if __name__ == "__main__":
    unittest.main()
