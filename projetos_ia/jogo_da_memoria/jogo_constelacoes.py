# -*- coding: utf-8 -*-
"""
Jogo da Memória das Constelações
=================================

Jogo da memória educativo: cada par é formado por uma carta com a FOTO da
constelação e uma carta com o NOME dela em português. As fotos trazem o nome
em latim impresso, que funciona como ponte para o aluno aprender a associação.

Requisitos: Python 3.9+ e Pillow. A interface é Tkinter (biblioteca padrão).
As faces das cartas são desenhadas com Pillow e apenas exibidas pelo Tk, o que
dá controle total da aparência (cantos arredondados, tipografia, animação).

Execução a partir do fonte:
    python jogo_constelacoes.py

Empacotamento (veja build.ps1):
    pyinstaller --onefile --windowed ...
"""

import io
import json
import os
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageFont, ImageTk

try:
    import winsound
except ImportError:      # o jogo é feito para Windows, mas não quebra fora dele
    winsound = None


# ---------------------------------------------------------------------------
# 1. Caminhos (funciona rodando do fonte e de dentro do .exe do PyInstaller)
# ---------------------------------------------------------------------------

def resource_path(rel):
    """Caminho de um recurso embutido.

    Quando o PyInstaller roda em --onefile, ele descompacta tudo numa pasta
    temporária cujo caminho fica em sys._MEIPASS. Rodando do fonte, a base é
    a pasta deste arquivo.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def pasta_dados_usuario():
    """Onde gravar os recordes.

    Nunca ao lado do executável: em --onefile aquilo é uma pasta temporária
    somente leitura, apagada ao fechar o jogo.
    """
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    caminho = os.path.join(base, "JogoConstelacoes")
    os.makedirs(caminho, exist_ok=True)
    return caminho


ARQUIVO_RECORDES = os.path.join(pasta_dados_usuario(), "recordes.json")


# ---------------------------------------------------------------------------
# 2. Aparência e constantes
# ---------------------------------------------------------------------------

COR_FUNDO = "#0b0e24"          # azul quase preto, o "céu"
COR_FUNDO_PAINEL = "#131740"
COR_CARTA_VERSO = "#1d2a6b"
COR_CARTA_NOME = "#f2f5ff"
COR_TEXTO_NOME = "#101538"
COR_TEXTO = "#e8ecff"
COR_TEXTO_FRACO = "#9aa6e0"
COR_DESTAQUE = "#ffd166"        # dourado
COR_ACERTO = "#4ade80"
COR_BOTAO = "#2b3a86"
COR_BOTAO_ATIVO = "#3b50b0"

NIVEIS = {
    "facil":   {"rotulo": "Fácil",   "pares": 6,  "colunas": 4, "linhas": 3},
    "medio":   {"rotulo": "Médio",   "pares": 10, "colunas": 5, "linhas": 4},
    "dificil": {"rotulo": "Difícil", "pares": 15, "colunas": 6, "linhas": 5},
}
ORDEM_NIVEIS = ["facil", "medio", "dificil"]

ESPACO = 12               # folga entre as cartas, em pixels
MS_COMPARACAO = 850       # quanto o par errado fica visível antes de desvirar
QUADROS_VIRADA = 7        # quadros de cada metade da animação de virar
MS_QUADRO = 16


# ---------------------------------------------------------------------------
# 3. Dados
# ---------------------------------------------------------------------------

def carregar_constelacoes():
    caminho = resource_path("constelacoes.json")
    with io.open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    validas, ausentes = [], []
    for c in dados:
        if os.path.exists(resource_path(c["imagem"])):
            validas.append(c)
        else:
            ausentes.append(c["id"])

    if ausentes:
        print("AVISO: imagens não encontradas para: %s" % ", ".join(ausentes))
    if len(validas) < max(n["pares"] for n in NIVEIS.values()):
        raise SystemExit(
            "Imagens insuficientes: %d encontradas, são necessárias %d."
            % (len(validas), max(n["pares"] for n in NIVEIS.values())))
    return validas


def ler_recordes():
    try:
        with io.open(ARQUIVO_RECORDES, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def gravar_recorde(nivel, segundos, jogadas):
    """Grava se for a melhor marca do nível. Devolve True se bateu o recorde."""
    recordes = ler_recordes()
    anterior = recordes.get(nivel)
    # critério: menos jogadas; empatou em jogadas, menor tempo
    melhor = (anterior is None
              or jogadas < anterior["jogadas"]
              or (jogadas == anterior["jogadas"] and segundos < anterior["segundos"]))
    if melhor:
        recordes[nivel] = {"segundos": round(segundos, 1), "jogadas": jogadas}
        try:
            with io.open(ARQUIVO_RECORDES, "w", encoding="utf-8") as f:
                json.dump(recordes, f, ensure_ascii=False, indent=2)
        except OSError:
            return False     # sem permissão de escrita: o jogo segue normal
    return melhor


# ---------------------------------------------------------------------------
# 4. Desenho das faces das cartas (Pillow)
# ---------------------------------------------------------------------------

_cache_fontes = {}


def fonte(tamanho, negrito=False):
    chave = (tamanho, negrito)
    if chave not in _cache_fontes:
        candidatos = (["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"] if negrito
                      else ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"])
        escolhida = None
        for nome in candidatos:
            try:
                escolhida = ImageFont.truetype(nome, tamanho)
                break
            except OSError:
                continue
        _cache_fontes[chave] = escolhida or ImageFont.load_default()
    return _cache_fontes[chave]


def _mascara_arredondada(w, h, raio):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=raio, fill=255)
    return m


def _achatar(img, w, h, raio, fundo):
    """Aplica cantos arredondados já mesclados com a cor de fundo do tabuleiro.

    Mesclar aqui, em vez de usar transparência no Tk, evita qualquer
    diferença de composição do canvas entre versões do Tk.
    """
    saida = Image.new("RGB", (w, h), fundo)
    saida.paste(img, (0, 0), _mascara_arredondada(w, h, raio))
    return saida


def _quebrar_linhas(texto, fnt, largura_max, desenho):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if desenho.textlength(teste, font=fnt) <= largura_max or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def face_verso(w, h):
    """Verso da carta: céu escuro com estrelinhas e um losango dourado."""
    raio = max(8, w // 14)
    img = Image.new("RGB", (w, h), COR_CARTA_VERSO)
    d = ImageDraw.Draw(img)

    # leve degradê vertical
    for y in range(h):
        f = y / max(1, h - 1)
        cor = tuple(int(a + (b - a) * f) for a, b in zip(
            (29, 42, 107), (15, 22, 66)))
        d.line([(0, y), (w, y)], fill=cor)

    # estrelas em posições fixas (semente constante = verso sempre igual)
    rnd = random.Random(20260911)
    for _ in range(int(w * h / 900)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        r = rnd.choice([0, 0, 0, 1, 1, 2])
        brilho = rnd.randint(120, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(brilho, brilho, min(255, brilho + 20)))

    # losango central
    cx, cy, s = w // 2, h // 2, max(10, w // 7)
    d.polygon([(cx, cy - s), (cx + s // 2, cy), (cx, cy + s), (cx - s // 2, cy)],
              outline=COR_DESTAQUE, width=max(2, w // 90))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=COR_DESTAQUE)

    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=raio,
                        outline="#3a4aa0", width=max(2, w // 100))
    return _achatar(img, w, h, raio, COR_FUNDO)


def face_foto(img_original, w, h, encontrada=False):
    raio = max(8, w // 14)
    img = img_original.resize((w, h), Image.LANCZOS)
    if encontrada:
        img = Image.blend(img, Image.new("RGB", (w, h), COR_FUNDO), 0.45)
    d = ImageDraw.Draw(img)
    borda = COR_ACERTO if encontrada else COR_DESTAQUE
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=raio,
                        outline=borda, width=max(2, w // 80))
    return _achatar(img, w, h, raio, COR_FUNDO)


def face_nome(nome, w, h, encontrada=False):
    raio = max(8, w // 14)
    fundo = "#cfe0c8" if encontrada else COR_CARTA_NOME
    img = Image.new("RGB", (w, h), fundo)
    d = ImageDraw.Draw(img)

    # o tamanho da fonte se adapta ao tamanho da carta e ao comprimento do nome
    tam = max(11, int(w / 7.5))
    while tam > 9:
        f = fonte(tam, negrito=True)
        linhas = _quebrar_linhas(nome, f, w - int(w * 0.16), d)
        altura_total = len(linhas) * int(tam * 1.22)
        if altura_total <= h - int(h * 0.22) and len(linhas) <= 4:
            break
        tam -= 1

    f = fonte(tam, negrito=True)
    linhas = _quebrar_linhas(nome, f, w - int(w * 0.16), d)
    passo = int(tam * 1.22)
    y = (h - len(linhas) * passo) // 2
    for linha in linhas:
        largura = d.textlength(linha, font=f)
        d.text(((w - largura) / 2, y), linha, font=f, fill=COR_TEXTO_NOME)
        y += passo

    borda = COR_ACERTO if encontrada else "#9fb0e8"
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=raio,
                        outline=borda, width=max(2, w // 80))
    return _achatar(img, w, h, raio, COR_FUNDO)


class CacheImagens:
    """Guarda os JPEGs abertos e as faces já renderizadas.

    As referências de ImageTk.PhotoImage precisam ficar vivas aqui: se o Python
    coletar o objeto, o Tk mostra um retângulo vazio no lugar da imagem. É a
    pegadinha clássica do Tkinter com imagens.
    """

    def __init__(self):
        self._originais = {}
        self._tk = {}

    def original(self, constelacao):
        cid = constelacao["id"]
        if cid not in self._originais:
            caminho = resource_path(constelacao["imagem"])
            with Image.open(caminho) as im:
                self._originais[cid] = im.convert("RGB").copy()
        return self._originais[cid]

    def tk_de_pil(self, chave, construir):
        if chave not in self._tk:
            self._tk[chave] = ImageTk.PhotoImage(construir())
        return self._tk[chave]

    def esquecer_faces(self):
        """Chamado ao mudar o tamanho das cartas."""
        self._tk.clear()


# ---------------------------------------------------------------------------
# 5. Carta
# ---------------------------------------------------------------------------

class Carta:
    def __init__(self, constelacao, tipo):
        self.constelacao = constelacao
        self.tipo = tipo               # "foto" ou "nome"
        self.estado = "baixo"          # "baixo" | "cima" | "encontrada"
        self.item = None               # id do objeto no Canvas
        self.cx = 0
        self.cy = 0

    @property
    def id_const(self):
        return self.constelacao["id"]


# ---------------------------------------------------------------------------
# 6. Som
# ---------------------------------------------------------------------------

def tocar(frequencia, duracao_ms, ligado):
    if not ligado or winsound is None:
        return
    # numa thread separada porque winsound.Beep bloqueia
    threading.Thread(target=_beep_seguro, args=(frequencia, duracao_ms),
                     daemon=True).start()


def _beep_seguro(f, ms):
    try:
        winsound.Beep(f, ms)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 7. Aplicação
# ---------------------------------------------------------------------------

class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jogo da Memória das Constelações")
        self.configure(bg=COR_FUNDO)
        self.geometry("1280x800")
        self.minsize(900, 620)

        try:
            self.iconbitmap(resource_path("icone.ico"))
        except Exception:
            pass       # sem ícone não é motivo para não abrir o jogo

        self.constelacoes = carregar_constelacoes()
        self.cache = CacheImagens()
        self.som_ligado = True

        self.container = tk.Frame(self, bg=COR_FUNDO)
        self.container.pack(fill="both", expand=True)
        self.tela = None
        self.mostrar_menu()

    # -- troca de telas ----------------------------------------------------
    def _trocar(self, construtor):
        if self.tela is not None:
            self.tela.destroy()
        self.tela = construtor(self.container, self)
        self.tela.pack(fill="both", expand=True)

    def mostrar_menu(self):
        self._trocar(TelaMenu)

    def mostrar_jogo(self, nivel):
        self._trocar(lambda pai, app: TelaJogo(pai, app, nivel))

    def mostrar_fim(self, nivel, segundos, jogadas, recorde):
        self._trocar(
            lambda pai, app: TelaFim(pai, app, nivel, segundos, jogadas, recorde))


# ---------------------------------------------------------------------------
# 8. Widgets auxiliares
# ---------------------------------------------------------------------------

def botao(pai, texto, comando, destaque=False, tamanho=13):
    return tk.Button(
        pai, text=texto, command=comando,
        font=("Segoe UI", tamanho, "bold" if destaque else "normal"),
        bg=COR_DESTAQUE if destaque else COR_BOTAO,
        fg=COR_TEXTO_NOME if destaque else COR_TEXTO,
        activebackground="#ffe08a" if destaque else COR_BOTAO_ATIVO,
        activeforeground=COR_TEXTO_NOME if destaque else COR_TEXTO,
        relief="flat", bd=0, padx=22, pady=11, cursor="hand2",
        highlightthickness=0)


def formatar_tempo(segundos):
    return "%02d:%02d" % (int(segundos) // 60, int(segundos) % 60)


# ---------------------------------------------------------------------------
# 9. Tela do menu
# ---------------------------------------------------------------------------

class TelaMenu(tk.Frame):
    def __init__(self, pai, app):
        super().__init__(pai, bg=COR_FUNDO)
        self.app = app

        tk.Label(self, text="✦", font=("Segoe UI", 40), fg=COR_DESTAQUE,
                 bg=COR_FUNDO).pack(pady=(52, 0))
        tk.Label(self, text="Jogo da Memória das Constelações",
                 font=("Segoe UI", 30, "bold"), fg=COR_TEXTO,
                 bg=COR_FUNDO).pack(pady=(6, 4))
        tk.Label(self, text="Encontre cada foto do céu e o nome da constelação que ela mostra.",
                 font=("Segoe UI", 13), fg=COR_TEXTO_FRACO, bg=COR_FUNDO).pack()

        caixa = tk.Frame(self, bg=COR_FUNDO)
        caixa.pack(pady=34)
        recordes = ler_recordes()
        for chave in ORDEM_NIVEIS:
            cfg = NIVEIS[chave]
            linha = tk.Frame(caixa, bg=COR_FUNDO)
            linha.pack(pady=7)
            botao(linha, "%s  ·  %d pares" % (cfg["rotulo"], cfg["pares"]),
                  lambda c=chave: app.mostrar_jogo(c),
                  destaque=(chave == "medio"), tamanho=14).pack(side="left")
            r = recordes.get(chave)
            texto = ("recorde: %s em %d jogadas" % (formatar_tempo(r["segundos"]), r["jogadas"])
                     if r else "sem recorde ainda")
            tk.Label(linha, text=texto, font=("Segoe UI", 10), fg=COR_TEXTO_FRACO,
                     bg=COR_FUNDO, width=26, anchor="w").pack(side="left", padx=(14, 0))

        rodape = tk.Frame(self, bg=COR_FUNDO)
        rodape.pack(side="bottom", pady=22)
        botao(rodape, "Como jogar", self.como_jogar, tamanho=11).pack(side="left", padx=6)
        botao(rodape, "Sair", app.destroy, tamanho=11).pack(side="left", padx=6)
        tk.Label(self, text="Imagens: NOIRLab/NSF/AURA — CC BY 4.0",
                 font=("Segoe UI", 9), fg="#66709e", bg=COR_FUNDO).pack(side="bottom")

    def como_jogar(self):
        messagebox.showinfo(
            "Como jogar",
            "As cartas ficam viradas para baixo.\n\n"
            "Cada par é formado por uma FOTO de uma constelação e pela carta "
            "com o NOME dela em português.\n\n"
            "Vire duas cartas por vez. Se combinarem, elas ficam abertas e "
            "aparece uma ficha com a curiosidade daquela constelação. Se não, "
            "elas viram de novo.\n\n"
            "Dica: as fotos trazem o nome em latim escrito. Use isso para "
            "descobrir o nome em português!\n\n"
            "Vença usando o menor número de jogadas que conseguir.",
            parent=self)


# ---------------------------------------------------------------------------
# 10. Tela do jogo
# ---------------------------------------------------------------------------

class TelaJogo(tk.Frame):
    def __init__(self, pai, app, nivel):
        super().__init__(pai, bg=COR_FUNDO)
        self.app = app
        self.nivel = nivel
        self.cfg = NIVEIS[nivel]

        # --- estado da partida
        sorteadas = random.sample(app.constelacoes, self.cfg["pares"])
        self.cartas = []
        for c in sorteadas:
            self.cartas.append(Carta(c, "foto"))
            self.cartas.append(Carta(c, "nome"))
        random.shuffle(self.cartas)

        self.primeira = None
        self.segunda = None
        self.bloqueado = False
        self.jogadas = 0
        self.pares_achados = 0
        self.inicio = None
        self.tarefa_relogio = None
        self.tarefa_redimensionar = None
        self.lado_carta = 0

        self._montar_layout()
        self.canvas.bind("<Configure>", self._ao_redimensionar)

    # -- construção da interface -------------------------------------------
    def _montar_layout(self):
        painel = tk.Frame(self, bg=COR_FUNDO_PAINEL, width=326)
        painel.pack(side="right", fill="y")
        painel.pack_propagate(False)
        self._montar_painel(painel)

        self.canvas = tk.Canvas(self, bg=COR_FUNDO, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)

    def _montar_painel(self, painel):
        tk.Label(painel, text=self.cfg["rotulo"].upper(), font=("Segoe UI", 11, "bold"),
                 fg=COR_DESTAQUE, bg=COR_FUNDO_PAINEL).pack(pady=(22, 2))
        tk.Label(painel, text="%d pares" % self.cfg["pares"], font=("Segoe UI", 10),
                 fg=COR_TEXTO_FRACO, bg=COR_FUNDO_PAINEL).pack()

        placar = tk.Frame(painel, bg=COR_FUNDO_PAINEL)
        placar.pack(pady=18)
        self.var_tempo = tk.StringVar(value="00:00")
        self.var_jogadas = tk.StringVar(value="0")
        self.var_pares = tk.StringVar(value="0 / %d" % self.cfg["pares"])
        for rotulo, var in (("Tempo", self.var_tempo), ("Jogadas", self.var_jogadas),
                            ("Pares", self.var_pares)):
            bloco = tk.Frame(placar, bg=COR_FUNDO_PAINEL)
            bloco.pack(side="left", padx=13)
            tk.Label(bloco, textvariable=var, font=("Segoe UI", 19, "bold"),
                     fg=COR_TEXTO, bg=COR_FUNDO_PAINEL).pack()
            tk.Label(bloco, text=rotulo, font=("Segoe UI", 9), fg=COR_TEXTO_FRACO,
                     bg=COR_FUNDO_PAINEL).pack()

        tk.Frame(painel, bg="#2a3268", height=1).pack(fill="x", padx=20, pady=(4, 16))

        # ficha da última constelação acertada
        self.ficha = tk.Frame(painel, bg=COR_FUNDO_PAINEL)
        self.ficha.pack(fill="both", expand=True, padx=20)
        self.var_f_nome = tk.StringVar(value="—")
        self.var_f_latim = tk.StringVar(value="")
        self.var_f_texto = tk.StringVar(
            value="Encontre um par para ver aqui a ficha da constelação.")

        tk.Label(self.ficha, textvariable=self.var_f_nome, font=("Segoe UI", 17, "bold"),
                 fg=COR_DESTAQUE, bg=COR_FUNDO_PAINEL, wraplength=280,
                 justify="left", anchor="w").pack(fill="x")
        tk.Label(self.ficha, textvariable=self.var_f_latim, font=("Segoe UI", 11, "italic"),
                 fg=COR_TEXTO_FRACO, bg=COR_FUNDO_PAINEL, anchor="w").pack(fill="x", pady=(0, 10))
        tk.Label(self.ficha, textvariable=self.var_f_texto, font=("Segoe UI", 11),
                 fg=COR_TEXTO, bg=COR_FUNDO_PAINEL, wraplength=280,
                 justify="left", anchor="nw").pack(fill="both", expand=True)

        botoes = tk.Frame(painel, bg=COR_FUNDO_PAINEL)
        botoes.pack(side="bottom", pady=20)
        self.btn_som = botao(botoes, "Som: ligado", self._alternar_som, tamanho=10)
        self.btn_som.pack(pady=4)
        botao(botoes, "Reiniciar", self._reiniciar, tamanho=10).pack(pady=4)
        botao(botoes, "Voltar ao menu", self._voltar, tamanho=10).pack(pady=4)

    # -- geometria ---------------------------------------------------------
    def _ao_redimensionar(self, evento=None):
        if self.tarefa_redimensionar:
            self.after_cancel(self.tarefa_redimensionar)
        self.tarefa_redimensionar = self.after(140, self._redesenhar_tudo)

    def _calcular_geometria(self):
        cols, lins = self.cfg["colunas"], self.cfg["linhas"]
        larg = max(self.canvas.winfo_width(), 200)
        alt = max(self.canvas.winfo_height(), 200)
        lado = min((larg - ESPACO * (cols + 1)) // cols,
                   (alt - ESPACO * (lins + 1)) // lins)
        lado = max(56, min(lado, 260))
        total_l = cols * lado + ESPACO * (cols - 1)
        total_a = lins * lado + ESPACO * (lins - 1)
        return lado, (larg - total_l) // 2, (alt - total_a) // 2

    def _redesenhar_tudo(self):
        self.tarefa_redimensionar = None
        lado, ox, oy = self._calcular_geometria()
        if lado != self.lado_carta:
            self.lado_carta = lado
            self.app.cache.esquecer_faces()
        self.canvas.delete("all")

        cols = self.cfg["colunas"]
        for i, carta in enumerate(self.cartas):
            lin, col = divmod(i, cols)
            carta.cx = ox + col * (lado + ESPACO) + lado // 2
            carta.cy = oy + lin * (lado + ESPACO) + lado // 2
            carta.item = self.canvas.create_image(
                carta.cx, carta.cy, image=self._imagem_da(carta))
            self.canvas.tag_bind(carta.item, "<Button-1>",
                                 lambda e, c=carta: self._clicar(c))
            self.canvas.tag_bind(carta.item, "<Enter>",
                                 lambda e: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(carta.item, "<Leave>",
                                 lambda e: self.canvas.config(cursor=""))

    # -- faces -------------------------------------------------------------
    def _imagem_da(self, carta, largura=None):
        """Devolve o PhotoImage da face atual da carta.

        `largura` menor que o lado é usada pela animação de virada.
        """
        lado = self.lado_carta
        larg = lado if largura is None else max(1, largura)
        estado = carta.estado
        if estado == "baixo":
            chave = ("verso", lado, larg)
            construir = lambda: self._comprimir(face_verso(lado, lado), larg, lado)
        else:
            encontrada = (estado == "encontrada")
            chave = (carta.id_const, carta.tipo, encontrada, lado, larg)
            if carta.tipo == "foto":
                original = self.app.cache.original(carta.constelacao)
                construir = lambda: self._comprimir(
                    face_foto(original, lado, lado, encontrada), larg, lado)
            else:
                construir = lambda: self._comprimir(
                    face_nome(carta.constelacao["nome"], lado, lado, encontrada), larg, lado)
        return self.app.cache.tk_de_pil(chave, construir)

    @staticmethod
    def _comprimir(img, larg, lado):
        return img if larg >= lado else img.resize((larg, lado), Image.BILINEAR)

    def _atualizar_carta(self, carta, largura=None):
        self.canvas.itemconfig(carta.item, image=self._imagem_da(carta, largura))

    # -- animações ---------------------------------------------------------
    def _animar_virada(self, carta, novo_estado, ao_terminar=None):
        """Vira a carta comprimindo-a na horizontal e voltando."""
        lado = self.lado_carta
        passos_fecha = [int(lado * (1 - (i + 1) / QUADROS_VIRADA))
                        for i in range(QUADROS_VIRADA)]

        def fechar(i=0):
            if i < len(passos_fecha):
                self._atualizar_carta(carta, max(1, passos_fecha[i]))
                self.after(MS_QUADRO, lambda: fechar(i + 1))
            else:
                carta.estado = novo_estado
                abrir(0)

        def abrir(i=0):
            if i < QUADROS_VIRADA:
                self._atualizar_carta(carta, max(1, int(lado * (i + 1) / QUADROS_VIRADA)))
                self.after(MS_QUADRO, lambda: abrir(i + 1))
            else:
                self._atualizar_carta(carta)
                if ao_terminar:
                    ao_terminar()

        fechar()

    def _tremer(self, cartas, ao_terminar=None):
        deslocamentos = [6, -6, 4, -4, 2, 0]

        def passo(i=0):
            if i < len(deslocamentos):
                for c in cartas:
                    self.canvas.coords(c.item, c.cx + deslocamentos[i], c.cy)
                self.after(28, lambda: passo(i + 1))
            else:
                for c in cartas:
                    self.canvas.coords(c.item, c.cx, c.cy)
                if ao_terminar:
                    ao_terminar()

        passo()

    # -- lógica do jogo ----------------------------------------------------
    def _clicar(self, carta):
        if self.bloqueado or carta.estado != "baixo":
            return
        if self.inicio is None:
            self.inicio = time.time()
            self._tique()

        tocar(660, 40, self.app.som_ligado)

        if self.primeira is None:
            self.primeira = carta
            self._animar_virada(carta, "cima")
        else:
            self.segunda = carta
            self.bloqueado = True
            self.jogadas += 1
            self.var_jogadas.set(str(self.jogadas))
            self._animar_virada(carta, "cima",
                                lambda: self.after(MS_COMPARACAO, self._comparar))

    def _comparar(self):
        a, b = self.primeira, self.segunda
        if a.id_const == b.id_const and a.tipo != b.tipo:
            self._acertou(a, b)
        else:
            self._errou(a, b)

    def _acertou(self, a, b):
        for c in (a, b):
            c.estado = "encontrada"
            self._atualizar_carta(c)
        self.pares_achados += 1
        self.var_pares.set("%d / %d" % (self.pares_achados, self.cfg["pares"]))
        self._mostrar_ficha(a.constelacao)
        tocar(1050, 110, self.app.som_ligado)
        self.primeira = self.segunda = None
        self.bloqueado = False
        if self.pares_achados == self.cfg["pares"]:
            self.after(600, self._vencer)

    def _errou(self, a, b):
        tocar(220, 130, self.app.som_ligado)

        def desvirar():
            restantes = [2]

            def uma_pronta():
                restantes[0] -= 1
                if restantes[0] == 0:
                    self.primeira = self.segunda = None
                    self.bloqueado = False

            for c in (a, b):
                self._animar_virada(c, "baixo", uma_pronta)

        self._tremer([a, b], desvirar)

    def _mostrar_ficha(self, constelacao):
        self.var_f_nome.set(constelacao["nome"])
        self.var_f_latim.set("%s  ·  %s" % (constelacao["nomeLatim"],
                                            constelacao["abreviacao"]))
        self.var_f_texto.set(constelacao.get("curiosidade", ""))

    # -- relógio -----------------------------------------------------------
    def _tique(self):
        if self.inicio is not None:
            self.var_tempo.set(formatar_tempo(time.time() - self.inicio))
            self.tarefa_relogio = self.after(250, self._tique)

    def _parar_relogio(self):
        if self.tarefa_relogio:
            self.after_cancel(self.tarefa_relogio)
            self.tarefa_relogio = None

    # -- fim ---------------------------------------------------------------
    def _vencer(self):
        segundos = time.time() - self.inicio
        self._parar_relogio()
        recorde = gravar_recorde(self.nivel, segundos, self.jogadas)
        self.app.mostrar_fim(self.nivel, segundos, self.jogadas, recorde)

    # -- botões ------------------------------------------------------------
    def _alternar_som(self):
        self.app.som_ligado = not self.app.som_ligado
        self.btn_som.config(text="Som: ligado" if self.app.som_ligado else "Som: desligado")

    def _reiniciar(self):
        self._parar_relogio()
        self.app.mostrar_jogo(self.nivel)

    def _voltar(self):
        self._parar_relogio()
        self.app.mostrar_menu()

    def destroy(self):
        self._parar_relogio()
        if self.tarefa_redimensionar:
            try:
                self.after_cancel(self.tarefa_redimensionar)
            except Exception:
                pass
        super().destroy()


# ---------------------------------------------------------------------------
# 11. Tela de fim
# ---------------------------------------------------------------------------

class TelaFim(tk.Frame):
    def __init__(self, pai, app, nivel, segundos, jogadas, recorde):
        super().__init__(pai, bg=COR_FUNDO)
        self.app = app

        tk.Label(self, text="✦", font=("Segoe UI", 36), fg=COR_DESTAQUE,
                 bg=COR_FUNDO).pack(pady=(96, 0))
        tk.Label(self, text="Você venceu!", font=("Segoe UI", 34, "bold"),
                 fg=COR_TEXTO, bg=COR_FUNDO).pack(pady=(8, 2))
        tk.Label(self, text="Nível %s" % NIVEIS[nivel]["rotulo"],
                 font=("Segoe UI", 13), fg=COR_TEXTO_FRACO, bg=COR_FUNDO).pack()

        numeros = tk.Frame(self, bg=COR_FUNDO)
        numeros.pack(pady=30)
        for valor, rotulo in ((formatar_tempo(segundos), "Tempo"),
                              (str(jogadas), "Jogadas")):
            bloco = tk.Frame(numeros, bg=COR_FUNDO)
            bloco.pack(side="left", padx=28)
            tk.Label(bloco, text=valor, font=("Segoe UI", 30, "bold"),
                     fg=COR_DESTAQUE, bg=COR_FUNDO).pack()
            tk.Label(bloco, text=rotulo, font=("Segoe UI", 10), fg=COR_TEXTO_FRACO,
                     bg=COR_FUNDO).pack()

        if recorde:
            tk.Label(self, text="Novo recorde neste nível!", font=("Segoe UI", 13, "bold"),
                     fg=COR_ACERTO, bg=COR_FUNDO).pack(pady=(0, 6))

        acoes = tk.Frame(self, bg=COR_FUNDO)
        acoes.pack(pady=16)
        botao(acoes, "Jogar de novo", lambda: app.mostrar_jogo(nivel),
              destaque=True).pack(side="left", padx=8)
        botao(acoes, "Voltar ao menu", app.mostrar_menu).pack(side="left", padx=8)


# ---------------------------------------------------------------------------
# 12. Início
# ---------------------------------------------------------------------------

def main():
    try:
        app = Aplicacao()
    except SystemExit:
        raise
    except Exception as erro:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Erro ao iniciar",
                             "Não foi possível iniciar o jogo:\n\n%s" % erro)
        raise
    app.mainloop()


if __name__ == "__main__":
    main()
