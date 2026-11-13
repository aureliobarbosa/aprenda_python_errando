import random

palavras = ["Legião Urbana", 
            "Titãs", 
            "Capital Inicial", 
            "Paralamas do Sucesso", 
            "O Trem da História", 
            "Sepultura", "Angra", 
            "Raul Seixas", 
            "Skank", 
            "Jota Quest", 
            "The Beatles", 
            "The Rolling Stones", 
            "Pink Floyd", 
            "Led Zeppelin", 
            "Queen", 
            "The Who", 
            "AC/DC", 
            "Metallica", 
            "Guns N' Roses", 
            "Nirvana",
            ]

folhas = 5
palavras_sorteadas = 15

for i in range(folhas):
    folha = random.sample(palavras, palavras_sorteadas)
    print(folha)
    