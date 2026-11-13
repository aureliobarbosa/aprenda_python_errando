peso = input("Entre com o peso")
x = 0
try:
    float(peso) / x
    # valor = float(peso)

    # print("seu peso é: ", valor)
except ValueError:
    print("Ocorreu um erro!")
    print("veja a mensagem dentro deste erro")
    print(ValueError)
