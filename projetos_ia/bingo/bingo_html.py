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
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo de Bandas - Folha {i+1}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #f0f0f0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }}
        .item {{
            background-color: #f9f9f9;
            border: 2px solid #ddd;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .item:hover {{
            background-color: #e8e8ff;
            border-color: #666;
        }}
        @media print {{
            body {{
                background-color: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Bingo de Bandas - Folha {i+1}</h1>
        <div class="grid">
"""
    
    for banda in folha:
        html_content += f'            <div class="item">{banda}</div>\n'
    
    html_content += """        </div>
    </div>
</body>
</html>"""
    
    with open(f"{i+1}.html", "w", encoding="utf-8") as arquivo:
        arquivo.write(html_content)