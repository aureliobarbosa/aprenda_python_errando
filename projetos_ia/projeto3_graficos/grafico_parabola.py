import matplotlib.pyplot as plt

plt.plot([-4,-3,-2, 1, 0, 1, 2, 3, 4], [16, 9, 4, 1, 0, 1, 4, 9, 16], 'o-')  # pontos da função quadrática

plt.title("Gráfico de uma função quadrática")
plt.xlabel("x") 
plt.ylabel("f(x)")
plt.grid(True)
plt.show()
