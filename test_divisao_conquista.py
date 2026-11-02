import math
import random
import unittest

from divisao_conquista import (
    contar_inversoes,
    contar_inversoes_forca_bruta,
    selecionar,
    mediana,
    mediana_ordenando,
    par_mais_proximo,
    par_mais_proximo_forca_bruta,
    karatsuba,
    multiplicacao_escolar,
    arranjo,
    combinacao,
)
from ordenacoes import bubble_sort


class TestContagemInversoes(unittest.TestCase):

    def test_exemplo_do_slide(self):
        # slide: 1 5 4 8 10 2 6 9 12 11 3 7 -> 22 inversões
        seq = [1, 5, 4, 8, 10, 2, 6, 9, 12, 11, 3, 7]
        ordenada, inv = contar_inversoes(seq)
        self.assertEqual(inv, 22)
        self.assertEqual(ordenada, sorted(seq))

    def test_casos_limite(self):
        self.assertEqual(contar_inversoes([])[1], 0)
        self.assertEqual(contar_inversoes([7])[1], 0)
        self.assertEqual(contar_inversoes(list(range(10)))[1], 0)
        self.assertEqual(contar_inversoes(list(range(10, 0, -1)))[1], 45)

    def test_igual_forca_bruta(self):
        rng = random.Random(1)
        for n in (2, 3, 10, 57, 300):
            seq = [rng.randint(0, 50) for _ in range(n)]
            self.assertEqual(contar_inversoes(seq)[1], contar_inversoes_forca_bruta(seq))

    def test_trocas_do_bubble_sort(self):
        seq = random.Random(2).sample(range(1000), 200)
        _, _, movimentacoes = bubble_sort(seq, chave=lambda x: x)
        self.assertEqual(movimentacoes // 2, contar_inversoes(seq)[1])


class TestMedianaDasMedianas(unittest.TestCase):

    def test_todos_os_k(self):
        rng = random.Random(3)
        for n in (1, 2, 5, 6, 26, 101):
            v = [rng.randint(0, 10) for _ in range(n)]   # muitos repetidos
            ordenado = sorted(v)
            for k in range(n):
                self.assertEqual(selecionar(v, k), ordenado[k])

    def test_mediana(self):
        self.assertEqual(mediana([5, 1, 3]), 3)
        self.assertEqual(mediana([4, 1, 3, 2]), 2.5)
        v = [random.Random(4).random() for _ in range(1001)]
        self.assertEqual(mediana(v), mediana_ordenando(v)[0])

    def test_com_chave(self):
        dados = [("a", 30), ("b", 10), ("c", 20)]
        self.assertEqual(selecionar(dados, 1, chave=lambda t: t[1]), ("c", 20))

    def test_k_invalido(self):
        with self.assertRaises(IndexError):
            selecionar([1, 2], 5)


class TestParMaisProximo(unittest.TestCase):

    def test_igual_forca_bruta(self):
        rng = random.Random(5)
        for n in (2, 3, 4, 10, 100, 500):
            pontos = [(rng.uniform(0, 100), rng.uniform(0, 100), i) for i in range(n)]
            d1 = par_mais_proximo(pontos)[0]
            d2 = par_mais_proximo_forca_bruta(pontos)[0]
            self.assertAlmostEqual(d1, d2)

    def test_pontos_repetidos_e_mesma_coluna(self):
        pontos = [(1, y, i) for i, y in enumerate([0, 5, 9, 14, 20])] + [(3, 3, 9), (3, 3, 10)]
        self.assertEqual(par_mais_proximo(pontos)[0], 0)
        coluna = [(0, y * 2, y) for y in range(20)]
        self.assertEqual(par_mais_proximo(coluna)[0], 2)

    def test_menos_de_dois_pontos(self):
        with self.assertRaises(ValueError):
            par_mais_proximo([(0, 0, 0)])


class TestKaratsuba(unittest.TestCase):

    def test_igual_multiplicacao_python(self):
        rng = random.Random(6)
        for digitos in (1, 5, 10, 50, 300, 2000):
            for _ in range(5):
                x = rng.randrange(10 ** digitos)
                y = rng.randrange(10 ** digitos)
                self.assertEqual(karatsuba(x, y), x * y)
                self.assertEqual(multiplicacao_escolar(x, y), x * y)

    def test_tamanhos_diferentes_e_zero(self):
        self.assertEqual(karatsuba(0, 10 ** 100), 0)
        self.assertEqual(multiplicacao_escolar(0, 12345), 0)
        x, y = 3 ** 2000, 7 ** 50
        self.assertEqual(karatsuba(x, y), x * y)

    def test_arranjo_e_combinacao(self):
        self.assertEqual(arranjo(4, 2), 12)
        self.assertEqual(combinacao(4, 2), 6)
        self.assertEqual(arranjo(4803, 4803), math.factorial(4803))
        self.assertEqual(combinacao(4803, 2401), math.comb(4803, 2401))
        self.assertEqual(combinacao(300, 10, multiplicar=multiplicacao_escolar),
                         math.comb(300, 10))
        self.assertEqual(combinacao(10, 10), 1)


if __name__ == "__main__":
    unittest.main()
