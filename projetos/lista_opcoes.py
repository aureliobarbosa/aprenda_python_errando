import sys


# Passo 1
# n = len(sys.argv)
# print('Número de parâmetros na chamada:', n)
# print('Parâmetros', sys.argv)

# print()
# opcoes = list(enumerate(sys.argv))
# print(opcoes)

# Passo 2
opcoes = enumerate(sys.argv)
for i, opcao in opcoes:
    print(i, opcao)




# Passo 3
# def main():
#     opcoes = enumerate(sys.argv)

#     for i, opcao in opcoes:
#         print(i, opcao)

# if __name__ == '__main__':
#     main()
