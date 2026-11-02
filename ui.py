LARGURA = 64


def linha(caractere="="):
    print(caractere * LARGURA)


def cabecalho(titulo, subtitulo=None):
    print()
    linha("=")
    print(titulo.center(LARGURA))
    if subtitulo:
        print(subtitulo.center(LARGURA))
    linha("=")


def secao(titulo):
    print(f"\n--- {titulo} ---")


def menu(titulo, opcoes, subtitulo=None, texto_sair="Voltar"):
    validas = {o[0] for o in opcoes if o and o[0]}
    while True:
        cabecalho(titulo, subtitulo)
        for opcao in opcoes:
            if opcao is None:
                print()
            elif opcao[0] == "":
                print(f"  {opcao[1]}")
            else:
                print(f"  {opcao[0]} - {opcao[1]}")
        print(f"\n  0 - {texto_sair}")
        linha("-")
        escolha = input("  Escolha uma opção: ").strip()
        if escolha == "0" or escolha in validas:
            return escolha
        print("  >> Opção inválida! Digite um dos números da lista.")


def pausar():
    input("\n  [Enter] para continuar...")


def ler_inteiro(mensagem, minimo, maximo, padrao=None):
    while True:
        dica = f" (Enter = {padrao})" if padrao is not None else " (Enter = voltar)"
        entrada = input(f"  {mensagem}{dica}: ").strip().replace(".", "")
        if entrada == "":
            return padrao
        if entrada.lstrip("-").isdigit() and minimo <= int(entrada) <= maximo:
            return int(entrada)
        print(f"  >> Digite um número inteiro entre {minimo} e {maximo}.")


def ler_texto(mensagem):
    return input(f"  {mensagem}: ").strip()


def confirmar(mensagem):
    return input(f"  {mensagem} (s/n): ").strip().casefold() in ("s", "sim", "y")


def tabela(cabecalhos, linhas, larguras):
    def formatar(valores):
        partes = []
        for valor, largura in zip(valores, larguras):
            texto = str(valor)
            partes.append(texto.ljust(-largura) if largura < 0 else texto.rjust(largura))
        return "  " + " ".join(partes)

    titulo = formatar(cabecalhos)
    print(titulo)
    print("  " + "-" * (len(titulo) - 2))
    for valores in linhas:
        print(formatar(valores))


def barra(valor, maximo, largura=30, caractere="#"):
    if maximo <= 0:
        return ""
    return caractere * max(0, round(valor / maximo * largura))


def ms(segundos):
    return f"{segundos * 1000:.2f} ms"


def numero(n):
    return f"{n:,}".replace(",", ".")
