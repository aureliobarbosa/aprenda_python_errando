""" fatorial.py
Implementa uma função que calcula o fatorial de um n úmero inteiro positivo.
"""


def fatorial(n):
    assert( n>= 0)
    if n == 0:
        return 1
    else:
        return n*fatorial(n-1)

x = int(input('Digite um número:'))

print('O fatorial de',x,'é',fatorial(x))