# Gerador de graficos

Aplicacao desktop local para abrir arquivos de texto com duas colunas e visualizar os dados em graficos de linha, barras ou pizza.

## Formato do arquivo

Aceita TXT, CSV e TSV. A primeira coluna e usada como rotulo e a segunda como valor numerico. Separadores aceitos: virgula, tabulacao ou espacos.

Exemplo:

```text
Janeiro 12
Fevereiro 18
Marco 9
```

Tambem e possivel usar uma linha de cabecalho; ela sera ignorada quando a segunda coluna nao for numerica.

## Executar no Windows

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py main.py
```

Para gerar um executavel:

```powershell
py -m pip install pyinstaller
pyinstaller --onefile --windowed main.py
```