import random

piadas = [
    "Por que o livro de matemática estava triste? Porque tinha muitos problemas.",
    "O que o zero disse para o oito? Que cinto bonito!",
    "Por que o computador foi ao médico? Porque estava com vírus.",
    "O que o oceano disse para a praia? Nada, só deu uma onda.",
    "Por que o espantalho ganhou um prêmio? Porque era o melhor no seu campo.",
    "O que o pato disse para a pata? Vem quá, vem quá!",
    "Por que a professora usava óculos escuros? Porque os alunos eram muito brilhantes.",
    "O que o caracol falou quando andou nas costas da tartaruga? Uhull!",
]

print(random.choice(piadas))

numeros = [42, 21, 35, 4, 51, 6, 7, 52, 99, 10]
numeros_sorteados = random.sample(numeros, 6)
print(numeros_sorteados)




