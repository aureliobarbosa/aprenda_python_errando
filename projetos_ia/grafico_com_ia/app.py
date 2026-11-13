import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class GraficoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Gráfico de dados")
        self.root.geometry("420x180")
        self.root.minsize(360, 160)

        self.dados: pd.DataFrame | None = None
        self.nome_arquivo = ""
        self.tipo_grafico = "linha"
        self.titulo = "Gráfico"
        self.rotulo_x = "x"
        self.rotulo_y = "y"
        self.cor = "#2f6f9f"
        self.janela_grafico: tk.Toplevel | None = None
        self.janela_configuracao: tk.Toplevel | None = None

        self._criar_interface()

    def _criar_interface(self) -> None:
        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Visualizador de dados x e y",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 18))

        botoes = ttk.Frame(frame)
        botoes.pack()

        ttk.Button(
            botoes,
            text="Abrir arquivo",
            command=self.abrir_arquivo,
        ).grid(row=0, column=0, padx=5)
        self.botao_configurar = ttk.Button(
            botoes,
            text="Configurar gráfico",
            command=self.abrir_configuracao,
            state="disabled",
        )
        self.botao_configurar.grid(row=0, column=1, padx=5)

        self.status = ttk.Label(frame, text="Nenhum arquivo aberto")
        self.status.pack(pady=(18, 0))

    def abrir_arquivo(self) -> None:
        pasta_dados = Path(__file__).resolve().parent / "dados"
        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo de dados",
            initialdir=pasta_dados if pasta_dados.is_dir() else Path(__file__).resolve().parent,
            filetypes=[
                ("Arquivos de dados", "*.txt *.dat *.csv"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if not caminho:
            return

        try:
            dados = pd.read_csv(
                caminho,
                sep=r"\s+",
                comment="#",
                header=None,
                names=["x", "y"],
                usecols=[0, 1],
                engine="python",
            )
            dados["x"] = pd.to_numeric(dados["x"], errors="raise")
            dados["y"] = pd.to_numeric(dados["y"], errors="raise")
        except (OSError, ValueError, pd.errors.ParserError) as erro:
            messagebox.showerror(
                "Não foi possível abrir o arquivo",
                f"Verifique se ele contém duas colunas numéricas.\n\n{erro}",
            )
            return

        if dados.empty:
            messagebox.showerror("Arquivo vazio", "O arquivo não possui dados para exibir.")
            return

        self.dados = dados
        self.nome_arquivo = Path(caminho).name
        self.status.configure(text=f"Arquivo: {self.nome_arquivo} ({len(dados)} pontos)")
        self.botao_configurar.configure(state="normal")
        self.exibir_grafico()

    def abrir_configuracao(self) -> None:
        if self.dados is None:
            return
        if self.janela_configuracao is not None and self.janela_configuracao.winfo_exists():
            self.janela_configuracao.focus_set()
            return

        janela = tk.Toplevel(self.root)
        janela.title("Configurar gráfico")
        janela.resizable(False, False)
        self.janela_configuracao = janela

        frame = ttk.Frame(janela, padding=18)
        frame.pack(fill="both", expand=True)

        tipo = tk.StringVar(value=self.tipo_grafico)
        titulo = tk.StringVar(value=self.titulo)
        rotulo_x = tk.StringVar(value=self.rotulo_x)
        rotulo_y = tk.StringVar(value=self.rotulo_y)
        cor = tk.StringVar(value=self.cor)

        ttk.Label(frame, text="Tipo de gráfico").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(
            frame,
            textvariable=tipo,
            values=("linha", "barra"),
            state="readonly",
            width=18,
        ).grid(row=0, column=1, sticky="ew", pady=5)

        campos = (
            ("Título", titulo),
            ("Rótulo de x", rotulo_x),
            ("Rótulo de y", rotulo_y),
            ("Cor", cor),
        )
        for linha, (rotulo, variavel) in enumerate(campos, start=1):
            ttk.Label(frame, text=rotulo).grid(row=linha, column=0, sticky="w", pady=5)
            ttk.Entry(frame, textvariable=variavel, width=21).grid(
                row=linha, column=1, sticky="ew", pady=5
            )

        def aplicar() -> None:
            self.tipo_grafico = tipo.get()
            self.titulo = titulo.get()
            self.rotulo_x = rotulo_x.get()
            self.rotulo_y = rotulo_y.get()
            self.cor = cor.get()
            self.exibir_grafico()
            janela.destroy()
            self.janela_configuracao = None

        ttk.Button(frame, text="Aplicar", command=aplicar).grid(
            row=5, column=0, columnspan=2, pady=(14, 0)
        )

    def exibir_grafico(self) -> None:
        if self.dados is None:
            return

        if self.janela_grafico is None or not self.janela_grafico.winfo_exists():
            self.janela_grafico = tk.Toplevel(self.root)
            self.janela_grafico.title("Gráfico")
            self.janela_grafico.geometry("760x520")
            self.canvas = FigureCanvasTkAgg(Figure(figsize=(7, 4.5)), self.janela_grafico)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            NavigationToolbar2Tk(self.canvas, self.janela_grafico)
        else:
            self.janela_grafico.focus_set()

        figura = self.canvas.figure
        figura.clear()
        eixo = figura.add_subplot(111)
        x = self.dados["x"]
        y = self.dados["y"]

        if self.tipo_grafico == "barra":
            eixo.bar(x, y, color=self.cor)
        else:
            eixo.plot(x, y, color=self.cor, marker="o")

        eixo.set_title(self.titulo)
        eixo.set_xlabel(self.rotulo_x)
        eixo.set_ylabel(self.rotulo_y)
        eixo.grid(True, alpha=0.25)
        figura.tight_layout()
        self.canvas.draw()
        self.janela_grafico.deiconify()
        self.janela_grafico.lift()
        self.janela_grafico.focus_force()
        self.status.configure(text=f"Gráfico exibido: {self.nome_arquivo}")


def main() -> None:
    root = tk.Tk()
    GraficoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()