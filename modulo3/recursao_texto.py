# import time
# Implementação da logica de um contador revor com for

# def corta_texto(n):
   
#     if n <= 0:
#         print('Blastoff!')  # lançou
#     else:
#         print(n)
#         countdown(n-1)


# n = int(input("Digite um número:"))
# # contador_com_entrada()
# countdown(n)

# texto = "A UnB é muito legal!"
# print(texto)
# tamanho = len(texto) # length()
# print("Caracteres: ", tamanho)

#print(texto[2], '\n', texto[0:5], '\n', texto[2:],'\n', texto[:7] )

def corta_texto(s):
    if len(s) <= 0:
        return None
    else:
        print(s)
        corta_texto(s[0:len(s)-1])
    

corta_texto("A UnB é muito legal!")

