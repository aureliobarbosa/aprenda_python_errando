
def conta_caracteres(caminho_arquivo):
    arquivo = open(caminho_arquivo, encoding='utf-8')
    n = 0
    for linha in arquivo:
        linha = linha.strip()
        n = n + len(linha)
    arquivo.close() # Extremamente importante

    return n

def conta_caracteres2(caminho_arquivo):
    n = 0
    with open(caminho_arquivo, encoding='utf-8') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            n = n + len(linha)
    return n

def count_chars(file, encoding='utf-8'):
    n = 0
    with open(file, encoding=encoding) as f:
        for line in f:
            n = n + len(line.strip())
    return n

caminho_arquivo =  '../dados/amostra-palavras.txt'
print(conta_caracteres2(caminho_arquivo))
print(count_chars(caminho_arquivo))
