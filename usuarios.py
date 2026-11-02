import csv
import os
import random

SEMENTE = 2026
QUANTIDADE_USUARIOS = 1000
FILMES_ASSISTIDOS_POR_USUARIO = 50
TAMANHO_ACERVO_POPULAR = 400

DIMENSOES = {
    "acao": ("Ação/Aventura", ["Action", "Adventure", "Science Fiction", "Fantasy",
                               "War", "Western", "Thriller", "Crime"]),
    "drama": ("Drama/Romance", ["Drama", "Romance", "History", "Music"]),
    "comedia": ("Comédia", ["Comedy"]),
    "terror": ("Terror/Mistério", ["Horror", "Mystery"]),
    "familia": ("Família/Animação", ["Family", "Animation"]),
}

CODIGOS_RANKING = [
    155,     # The Dark Knight
    597,     # Titanic
    862,     # Toy Story
    11036,   # The Notebook
    157336,  # Interstellar
    138843,  # The Conjuring
    18785,   # The Hangover
    76341,   # Mad Max: Fury Road
    13,      # Forrest Gump
    680,     # Pulp Fiction
]

NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabriela", "Hugo",
         "Isabela", "João", "Karina", "Lucas", "Mariana", "Nicolas", "Olivia",
         "Paulo", "Rafaela", "Samuel", "Tatiane", "Victor", "Yasmin", "Pedro",
         "Beatriz", "Caio", "Larissa", "Mateus", "Natália", "Otávio", "Renata", "Thiago"]


def dimensoes_do_filme(filme):
    return [d for d, (_, generos) in DIMENSOES.items()
            if any(g in filme.genero for g in generos)]


class Usuario:
    def __init__(self, codigo, nome, afinidades):
        self.codigo = codigo
        self.nome = nome
        self.afinidades = afinidades    
        self.avaliacoes = {}             

    def __str__(self):
        return f"{self.nome} (#{self.codigo:04d})"

    def ranking(self, codigos):
        return sorted(codigos, key=lambda c: (-self.avaliacoes[c], c))

    def ponto_no_mapa(self, filmes_por_codigo):
        somas = {"acao": [0.0, 0], "drama": [0.0, 0]}
        for codigo, nota in self.avaliacoes.items():
            for d in dimensoes_do_filme(filmes_por_codigo[codigo]):
                if d in somas:
                    somas[d][0] += nota
                    somas[d][1] += 1
        x = somas["acao"][0] / somas["acao"][1] * 10 if somas["acao"][1] else 50.0
        y = somas["drama"][0] / somas["drama"][1] * 10 if somas["drama"][1] else 50.0
        return (x, y, self)


def _nota_do_usuario(filme, afinidades, rng):
    dims = dimensoes_do_filme(filme)
    afinidade = sum(afinidades[d] for d in dims) / len(dims) if dims else 0.5
    base = filme.nota if filme.nota > 0 else 6.0
    nota = base + 6 * (afinidade - 0.5) + rng.gauss(0, 0.7)
    return round(min(10.0, max(0.5, nota)), 1)


def gerar_usuarios(filmes, quantidade=QUANTIDADE_USUARIOS, semente=SEMENTE):
    rng = random.Random(semente)
    por_codigo = {f.codigo: f for f in filmes}
    filmes_ranking = [por_codigo[c] for c in CODIGOS_RANKING if c in por_codigo]

    candidatos = [f for f in filmes if f.codigo not in CODIGOS_RANKING]
    candidatos.sort(key=lambda f: -f.votos)
    acervo = candidatos[:TAMANHO_ACERVO_POPULAR]

    usuarios = []
    for i in range(1, quantidade + 1):
        afinidades = {d: rng.random() for d in DIMENSOES}
        usuario = Usuario(i, rng.choice(NOMES), afinidades)
        assistidos = filmes_ranking + rng.sample(acervo, FILMES_ASSISTIDOS_POR_USUARIO)
        for filme in assistidos:
            usuario.avaliacoes[filme.codigo] = _nota_do_usuario(filme, afinidades, rng)
        usuarios.append(usuario)
    return usuarios


def avaliacoes_da_comunidade(filme, maximo=2000):
    rng = random.Random(filme.codigo)
    quantidade = min(max(filme.votos, 50), maximo)
    media = filme.nota if filme.nota > 0 else 6.0
    return [int(min(10, max(0, round(rng.gauss(media, 1.3))))) for _ in range(quantidade)]


def exportar_usuarios_csv(usuarios, filmes_por_codigo, caminho=None):
    caminho = caminho or os.path.join(os.path.dirname(__file__), "usuarios.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["usuario", "nome"] + [f"afinidade_{d}" for d in DIMENSOES]
                          + ["mapa_x_acao", "mapa_y_drama", "filme", "titulo", "nota"])
        for u in usuarios:
            x, y, _ = u.ponto_no_mapa(filmes_por_codigo)
            fixos = [u.codigo, u.nome] + [f"{u.afinidades[d]:.3f}" for d in DIMENSOES] \
                + [f"{x:.2f}", f"{y:.2f}"]
            for codigo, nota in u.avaliacoes.items():
                escritor.writerow(fixos + [codigo, filmes_por_codigo[codigo].titulo, nota])
    return caminho
