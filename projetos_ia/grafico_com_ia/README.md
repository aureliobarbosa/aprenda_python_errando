# Visualizador de gráficos

Aplicativo simples para abrir dados com duas colunas (`x` e `y`) e exibir gráficos de linha ou barra.

## Formato do arquivo

Espaços ou tabulações podem separar as colunas. Linhas iniciadas por `#` são ignoradas:

```text
# x  y
1     2
1.2   3
2     4
```

## Executar

No terminal, dentro desta pasta:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Se o VS Code estiver usando outro interpretador Python, selecione o mesmo interpretador usado para instalar as dependências.

## Usar

1. Clique em **Abrir arquivo** e escolha um arquivo `.txt`, `.dat` ou `.csv`.
2. Clique em **Configurar gráfico** para escolher linha ou barra, título, rótulos e cor.
3. Use a barra do Matplotlib para zoom, movimentação e salvamento da imagem.