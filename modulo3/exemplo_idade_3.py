



idade = int(input("Digite a sua idade:"))

# condições diferentes: bebe, jovem, adulto, idoso
# assert( idade >= 0 )
if idade <= 0:
    print('A idade não pode ser negativa!')
    exit()

# Exemplo de elifs aninhados
if idade < 3:
    r = "bebê"
elif 3 <= idade < 23:
    r = "jovem"
elif 23 <= idade < 65: # (23 <= idade ) and (idade < 65) 
    r = "adulto"
elif 65 <= idade < 90:
    r = "idoso"
else:
    r = 'matusalém'

print(r)

if (idade < 18) or (idade > 90):
    print("Não pode beber.")
else:
    print("pode beber")



# if idade > 65:
#     print('Idoso.')
# else:
#     print('Jovem.')

