operacao = input("""
Este programa realiza uma operação entre dois números. 
Digite a operação que você deseja realizar:
+ para adição
- para subtração
* para multiplicação
/ para divisão
""")

# print(operacao)
if operacao not in "+-*/":
    print(f"Operação '{operacao}' é inválida!")
    exit()

a = int(input('Entre com o primeiro número: '))
b = int(input('Entre com o segundo número: '))

if operacao == '+':
    resultado = a + b
elif operacao == '-':
    resultado = a - b
elif operacao == '*':
    resultado = a * b
elif operacao == '/':
    resultado = a / b

print('Este é o resultado da operação solicitada:')
print(f'{a} {operacao} {b} = {resultado}')