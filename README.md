# G34_Dividir_e_Conquistar_2026.2

Trabalho 3<br>
Conteúdo da Disciplina: Dividir e Conquistar<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 21/1063256  |  Victor Hugo Rodrigues Guimarães |
| 21/1063229  |  Pedro Henrique dos Santos Ferreira |

## Sobre
O trabalho é uma plataforma de streaming de terminal construída sobre o catálogo
real de 4.803 filmes (`movies.csv`). O sistema continua com as funcionalidades
de **busca** e **ordenação** do Trabalho EDA2 e ganha quatro funcionalidades novas, cada uma
movida por um algoritmo de **divisão e conquista**:

| Funcionalidade | Algoritmo | Complexidade | Força bruta comparada |
| -- | -- | -- | -- |
| Recomendação por gosto | Contagem de Inversões | O(n log n) | O(n²) |
| Mapa de gostos (almas gêmeas) | Par de Pontos Mais Próximos | O(n log n) | O(n²) |
| Nota robusta / review bombing | Mediana das Medianas | O(n) | Heap Sort O(n log n) |
| Planejador de maratona | Karatsuba | O(n^1.585) | Multiplicação escolar O(n²) |

Todos os algoritmos estão em `divisao_conquista.py`, cada um ao lado da sua versão de
força bruta, usada para **validar** o resultado e **comparar** o desempenho.

### 1. Recomendação por gosto - Contagem de Inversões
O usuário ranqueia 10 filmes conhecidos. O sistema conta as **inversões** entre o ranking
dele e o de cada um dos 1.000 usuários simulados: 0 inversões = gosto idêntico,
45 = gosto oposto. Também é possível comparar dois usuários e ver exatamente
quais pares de filmes estão invertidos.

### 2. Mapa de gostos - Par de Pontos Mais Próximos
Cada usuário vira um ponto (x = gosto por Ação/Aventura, y = gosto por Drama/Romance),
calculado a partir das notas que ele deu. O algoritmo encontra os dois usuários com gosto
mais parecido, desenha o mapa no terminal e sugere filmes entre eles.

### 3. Nota robusta - Mediana das Medianas
Calcula a mediana das avaliações de um filme em tempo linear. A demonstração de
**review bombing** injeta centenas de notas 0, a média despenca e a mediana quase não muda.
O mesmo algoritmo de seleção calcula percentis do catálogo real (duração, orçamento,
popularidade e nota) sem ordenar os dados.

### 4. Planejador de maratona - Karatsuba
Calcula quantas maratonas de k filmes podem ser montadas com os filmes de um gênero:
**arranjo** A(n,k) (em ordem, sem repetir) e **combinação** C(n,k) (só a lista).
Com o catálogo inteiro o resultado (4803!) tem **15.599 dígitos**. Todos os produtos são
feitos com Karatsuba, organizados numa árvore de produtos.
A implementação usa base 2 (divide os números deslocando bits).

### Dados simulados
O CSV só tem a nota **média** de cada filme. Para ter usuários e notas individuais, o
programa gera (`usuarios.py`) 1.000 usuários com afinidades por gênero e as notas que eles
dariam, usando uma **semente fixa**: toda execução gera exatamente os mesmos dados. Eles podem
ser exportados para `usuarios.csv` pelo menu *Dados*.

## Estrutura

| Arquivo | Conteúdo |
| -- | -- |
| `main.py` | Menu principal, busca, ordenação e comparativos |
| `streaming.py` | Telas das 4 funcionalidades de divisão e conquista |
| `divisao_conquista.py` | Os 4 algoritmos + versões de força bruta |
| `usuarios.py` | Geração dos usuários e avaliações simulados |
| `filmes.py` | Leitura do `movies.csv` |
| `buscas.py` / `ordenacoes.py` | Algoritmos do Trabalho 2 |
| `ui.py` | Funções de interface do terminal (menus, tabelas) |
| `test_*.py` | Testes automatizados |

## Menu
```
  Catálogo:
  1 - Buscar filmes
  2 - Ordenar catálogo

  Divisão e conquista:
  3 - Recomendação por gosto      [Contagem de Inversões]
  4 - Mapa de gostos              [Par de Pontos Mais Próximos]
  5 - Nota robusta                [Mediana das Medianas]
  6 - Planejador de maratona      [Karatsuba]

  7 - Comparativos de desempenho
  8 - Dados (catálogo e usuários)

  0 - Sair
```
Em todas as telas, **0 volta** para o menu anterior e **Enter** usa o valor sugerido.

## Screenshots

### Trabalho 2
![bubble](imagens/bubble.png)
![insertion](imagens/insertion.png)
![comparativo](imagens/comparativo.png)

## Vídeo
- Trabalho 3: (adicionar link)
- Trabalho 2: https://youtu.be/o7OGsmxZY_U

## Instalação
Linguagem: Python 3.8+ (apenas biblioteca padrão, nada para instalar).

## Uso
```
python main.py
```
Testes:
```
python -m unittest
```
