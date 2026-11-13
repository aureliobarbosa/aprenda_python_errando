# -*- coding: utf-8 -*-
"""Prova de fogo: Tkinter + Pillow + PyInstaller no Python 3.14 / Tcl-Tk 9.0.
Grava PRONTO.txt no instante em que a janela fica visivel, para medir o tempo
real de abertura (inclui a descompactacao do --onefile)."""
import os, sys, time, tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

raiz = tk.Tk()
raiz.title("Teste de empacotamento")
raiz.configure(bg="#0d1030")

caminho = resource_path(os.path.join("imagens", "constelacoes", "crux.jpg"))
img = Image.open(caminho).resize((360, 360), Image.LANCZOS)
foto = ImageTk.PhotoImage(img)

tk.Label(raiz, image=foto, bg="#0d1030").pack(padx=16, pady=(16, 8))
tk.Label(raiz, text="Python %s | Tcl/Tk %s | congelado: %s" % (
    sys.version.split()[0], raiz.tk.call("info", "patchlevel"),
    getattr(sys, "frozen", False)), fg="#cfd6ff", bg="#0d1030").pack()
ttk.Button(raiz, text="Fechar", command=raiz.destroy).pack(pady=12)

def marcar_pronto():
    alvo = os.environ.get("TESTE_MARCADOR")
    if alvo:
        with open(alvo, "w") as f:
            f.write("%.6f\n" % time.time())
    if os.environ.get("TESTE_AUTOFECHAR") == "1":
        raiz.after(600, raiz.destroy)

raiz.update_idletasks()
raiz.after_idle(marcar_pronto)
raiz.mainloop()
