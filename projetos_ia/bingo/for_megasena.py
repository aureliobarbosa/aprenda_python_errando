import random

numeros = list(range(1,61))

numero_de_sorteios = 5
numeros_sorteados = 6

for i in range(numero_de_sorteios):
    numeros = random.sample(numeros, numeros_sorteados)
    print(numeros)
    