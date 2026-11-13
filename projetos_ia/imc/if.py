nome = "Adriana Calcanhoto"
# nome = nome.replace(' ','')

print(nome.lower())

vogais = ['a', 'e', 'i', 'o', 'u']

vogais_encontradas = []
consoantes_encontradas = []
for letra in nome.lower().replace(' ',''):
    if letra in vogais:
        vogais_encontradas.append(letra)
    else:
        consoantes_encontradas.append(letra)

print('vogais: ', vogais_encontradas)
print('consoantes: ', consoantes_encontradas)






    

