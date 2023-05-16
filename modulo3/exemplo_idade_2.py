
idade = int(input("Digite a sua idade:"))


# condições diferentes: bebe, jovem, adulto, idoso
# assert( idade >= 0 )
if idade <= 0:
    print('A idade não pode ser negativa!')
    exit()

# Exemplo de ifs aninhados
if idade < 3:
    r = "bebê"
else: 
    if idade < 23:
        r = "jovem"
    else:
        if idade < 65:
            r = "adulto"
        else:
            r = "idoso"

print(r)

# if idade > 65:
#     print('Idoso.')
# else:
#     print('Jovem.')

