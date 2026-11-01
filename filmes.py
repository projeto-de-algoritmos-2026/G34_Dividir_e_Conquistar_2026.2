import csv
import os

CAMINHO_CSV_PADRAO = os.path.join(os.path.dirname(__file__), "movies.csv")


class Filme:
    def __init__(self, codigo, titulo, ano, genero, nota=0.0, votos=0,
                 popularidade=0.0, duracao=0, orcamento=0):
        self.codigo = codigo
        self.titulo = titulo
        self.ano = ano
        self.genero = genero
        
        self.nota = nota                 
        self.votos = votos                
        self.popularidade = popularidade  
        self.duracao = duracao            
        self.orcamento = orcamento       

    def __str__(self):
        return f"[{self.codigo:>7}] {self.titulo} ({self.ano}) - {self.genero}"

    def resumo(self):
        return f"{self.titulo} ({self.ano}) - nota {self.nota:.1f}"


def _extrair_ano(release_date):
    """'2009-12-10' -> 2009. Datas ausentes/mal formadas viram 0."""
    release_date = (release_date or "").strip()
    if len(release_date) >= 4 and release_date[:4].isdigit():
        return int(release_date[:4])
    return 0


def _numero(texto, tipo=float):
    """Converte texto do CSV em número; vazio ou inválido vira 0."""
    try:
        return tipo(float(texto))
    except (TypeError, ValueError):
        return tipo(0)


def carregar_filmes(caminho_csv=CAMINHO_CSV_PADRAO):
    filmes = []
    with open(caminho_csv, newline="", encoding="utf-8") as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        for linha in leitor:
            genero = linha["genres"].strip() or "Desconhecido"
            filmes.append(
                Filme(
                    codigo=int(linha["id"]),
                    titulo=linha["title"],
                    ano=_extrair_ano(linha["release_date"]),
                    genero=genero,
                    nota=_numero(linha["vote_average"]),
                    votos=_numero(linha["vote_count"], int),
                    popularidade=_numero(linha["popularity"]),
                    duracao=_numero(linha["runtime"], int),
                    orcamento=_numero(linha["budget"], int),
                )
            )
    return filmes
