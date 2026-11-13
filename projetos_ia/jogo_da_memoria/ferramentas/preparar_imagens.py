# -*- coding: utf-8 -*-
"""Utilitario de build (roda uma vez, nao faz parte do jogo).

Gera as imagens que vao embutidas no executavel:
  imagens/constelacoes/*.jpg  (1280px, originais do NOIRLab)  ->
  imagens/cartas/*.jpg        (400px, ~54 KB cada)
e o icone do aplicativo a partir do Cruzeiro do Sul.

Reduz o conjunto de ~27,8 MB para ~2,1 MB, que e o que torna viavel
um executavel --onefile pequeno.
"""
import os, sys, glob
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAIS = os.path.join(RAIZ, "imagens", "constelacoes")
CARTAS = os.path.join(RAIZ, "imagens", "cartas")
LADO = 400
QUALIDADE = 82


def preparar_cartas():
    os.makedirs(CARTAS, exist_ok=True)
    arquivos = sorted(glob.glob(os.path.join(ORIGINAIS, "*.jpg")))
    if not arquivos:
        sys.exit("ERRO: nenhuma imagem em %s" % ORIGINAIS)
    total = 0
    for caminho in arquivos:
        destino = os.path.join(CARTAS, os.path.basename(caminho))
        with Image.open(caminho) as im:
            im = im.convert("RGB")
            # as imagens do NOIRLab ja sao quadradas; o crop central abaixo
            # so age se alguma nao for, mantendo o centro da constelacao
            lado = min(im.size)
            esq = (im.width - lado) // 2
            topo = (im.height - lado) // 2
            im = im.crop((esq, topo, esq + lado, topo + lado))
            im = im.resize((LADO, LADO), Image.LANCZOS)
            im.save(destino, "JPEG", quality=QUALIDADE, optimize=True)
        total += os.path.getsize(destino)
    print("cartas: %d imagens de %dx%d -> %.1f MB" % (len(arquivos), LADO, LADO, total / 1048576))
    return len(arquivos)


def preparar_icone():
    origem = os.path.join(ORIGINAIS, "crux.jpg")
    if not os.path.exists(origem):
        print("AVISO: crux.jpg nao encontrado, icone nao gerado")
        return
    destino = os.path.join(RAIZ, "icone.ico")
    with Image.open(origem) as im:
        im = im.convert("RGB")
        # recorte central: em icones pequenos o Cruzeiro precisa preencher o quadro
        lado = int(min(im.size) * 0.62)
        esq = (im.width - lado) // 2
        topo = (im.height - lado) // 2
        im = im.crop((esq, topo, esq + lado, topo + lado))
        im.save(destino, "ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("icone: %s (%.0f KB)" % (os.path.basename(destino), os.path.getsize(destino) / 1024))


if __name__ == "__main__":
    preparar_cartas()
    preparar_icone()
    print("pronto.")
