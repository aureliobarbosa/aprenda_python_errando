import time
# Implementação da logica de um contador revor com for

def contador_com_entrada():
    n = int(input("Digite um número inteiro (>0): "))
    assert(n>0)
    print("Iniciando contagem regressiva:")
    for i in range(n,-1,-1):
        print(i)
        time.sleep(1)

    print("Acabou!")

def countdown(n):
    
    if n <= 0:
        print('Blastoff!')  # lançou
    else:
        print(n)
        countdown(n-1)


n = int(input("Digite um número:"))
# contador_com_entrada()
countdown(n)

