# Página. 111

print("Eco. Um programa que te repete!\n"
      "Para sair digite cansei, como abaixo:\n"
      "> cansei\n\n"
      )

while True:
    entrada = input(">")
    if entrada == 'cansei':
        break
    print(entrada, end='\n\n')

print("Eu também cansei! Até mais.\n")