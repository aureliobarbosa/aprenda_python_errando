
# Exercício 3.1
#  Escreva uma função chamada right_justify, 
# que receba uma string chamada s como parâmetro 
# e exiba a string com espaços suficientes 
# à frente para que a última letra da string 
# esteja na coluna 70 da tela:
# >>> right_justify('monty')
# Dica: Use concatenação de strings e repetição. 
# Além disso, o Python oferece uma função integrada chamada 
# len, que apresenta o comprimento de uma string, então o 
# valor de len('monty') é 5.              
# 
#                                                  monty
# sintaxe:
# def nome_da_funcao(argumento):
#     ...

def right_justify(s):
    tamanho_s = len(s)
    tamanho_complemento = 70 - tamanho_s
    
    complemento = " "*tamanho_complemento
    resultado = complemento + s
    print(resultado)

def right_justify2(s,n=70):
    """
    Justifica um string s em um trecho com n caracteres. 
    n=70 por padrão.
    """
    return ( n - len(s) )*" " + s

right_justify("Teste do cabrobró!")

print( right_justify2( "Teste do cabrobró!") )
