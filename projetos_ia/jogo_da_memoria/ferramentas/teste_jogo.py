# -*- coding: utf-8 -*-
"""Teste automatizado do jogo: desenha as faces e joga partidas inteiras
sozinho, conferindo as regras. Não faz parte do executável.

Uso:  .venv\\Scripts\\python.exe ferramentas\\teste_jogo.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jogo_constelacoes as J   # noqa: E402

falhas = []


def checar(condicao, descricao):
    print(("  OK   " if condicao else "  FALHA") + "  " + descricao)
    if not condicao:
        falhas.append(descricao)


# ---------------------------------------------------------------------------
print("\n[1] Dados")
consts = J.carregar_constelacoes()
checar(len(consts) == 40, "40 constelações carregadas (%d)" % len(consts))
checar(all(c.get("curiosidade") for c in consts), "todas têm curiosidade")
checar(all(os.path.exists(J.resource_path(c["imagem"])) for c in consts),
       "todas as imagens existem")
ids = [c["id"] for c in consts]
checar(len(ids) == len(set(ids)), "sem ids repetidos")

# ---------------------------------------------------------------------------
print("\n[2] Desenho das faces (Pillow)")
t0 = time.time()
for lado in (96, 160, 260):
    v = J.face_verso(lado, lado)
    checar(v.size == (lado, lado), "verso %dpx" % lado)
for c in consts[:3]:
    original = J.Image.open(J.resource_path(c["imagem"])).convert("RGB")
    f = J.face_foto(original, 200, 200)
    n = J.face_nome(c["nome"], 200, 200)
    checar(f.size == (200, 200) and n.size == (200, 200),
           "faces de %s" % c["nome"])
# nome muito comprido não pode estourar a carta
longo = J.face_nome("Áries (o Carneiro) com nome exageradamente comprido", 120, 120)
checar(longo.size == (120, 120), "nome comprido cabe numa carta pequena")
print("  (%.0f ms para os desenhos acima)" % ((time.time() - t0) * 1000))

# ---------------------------------------------------------------------------
print("\n[3] Partida completa, nível por nível")

app = J.Aplicacao()
app.geometry("1280x800")


def jogar_nivel(nivel, ao_terminar):
    """Abre o nível e joga sozinho, sempre casando os pares certos."""
    app.mostrar_jogo(nivel)
    tela = app.tela
    app.update()
    tela._redesenhar_tudo()
    app.update()

    cfg = J.NIVEIS[nivel]
    checar(len(tela.cartas) == cfg["pares"] * 2,
           "%s: %d cartas" % (cfg["rotulo"], cfg["pares"] * 2))
    fotos = [c for c in tela.cartas if c.tipo == "foto"]
    nomes = [c for c in tela.cartas if c.tipo == "nome"]
    checar(len(fotos) == len(nomes) == cfg["pares"],
           "%s: metade foto, metade nome" % cfg["rotulo"])
    checar(sorted(c.id_const for c in fotos) == sorted(c.id_const for c in nomes),
           "%s: cada foto tem exatamente um nome" % cfg["rotulo"])

    # um erro de propósito, para exercitar o caminho do par errado
    estado = {"fase": "erro", "restantes": list(fotos), "erros_feitos": 0}

    def passo():
        if tela.bloqueado:
            app.after(30, passo)
            return

        if estado["fase"] == "erro":
            if len(fotos) >= 2:
                a = fotos[0]
                b = next(n for n in nomes if n.id_const != a.id_const)
                tela._clicar(a)
                tela._clicar(b)
            estado["fase"] = "acertos"
            app.after(30, passo)
            return

        if not estado["restantes"]:
            ao_terminar(tela)
            return

        foto = estado["restantes"].pop()
        nome = next(n for n in nomes if n.id_const == foto.id_const)
        tela._clicar(foto)
        tela._clicar(nome)
        app.after(30, passo)

    app.after(30, passo)


def conferir_fim(nivel, tela, proximo):
    cfg = J.NIVEIS[nivel]
    checar(tela.pares_achados == cfg["pares"],
           "%s: achou os %d pares" % (cfg["rotulo"], cfg["pares"]))
    checar(tela.jogadas == cfg["pares"] + 1,
           "%s: %d jogadas (%d acertos + 1 erro proposital)"
           % (cfg["rotulo"], tela.jogadas, cfg["pares"]))
    checar(all(c.estado == "encontrada" for c in tela.cartas),
           "%s: todas as cartas ficaram abertas" % cfg["rotulo"])
    checar(tela.inicio is not None, "%s: cronômetro começou" % cfg["rotulo"])

    def depois():
        checar(isinstance(app.tela, J.TelaFim),
               "%s: foi para a tela de vitória" % cfg["rotulo"])
        proximo()

    app.after(900, depois)


def encerrar():
    print("\n[4] Regras específicas")
    app.mostrar_jogo("facil")
    tela = app.tela
    app.update()
    tela._redesenhar_tudo()
    app.update()

    alvo = tela.cartas[0]
    tela._clicar(alvo)
    checar(tela.primeira is alvo, "primeira carta vira")
    tela._clicar(alvo)
    checar(tela.jogadas == 0, "clicar de novo na mesma carta não conta jogada")

    tela.bloqueado = True
    outra = tela.cartas[1]
    tela._clicar(outra)
    checar(outra.estado == "baixo", "bloqueado: terceira carta não vira")
    tela.bloqueado = False

    encontrada = tela.cartas[2]
    encontrada.estado = "encontrada"
    tela._clicar(encontrada)
    checar(tela.segunda is None or tela.segunda is not encontrada,
           "carta já encontrada não pode ser clicada")

    app.after(60, app.destroy)


niveis = list(J.ORDEM_NIVEIS)


def proximo_nivel():
    if not niveis:
        encerrar()
        return
    nivel = niveis.pop(0)
    jogar_nivel(nivel, lambda tela: conferir_fim(nivel, tela, proximo_nivel))


app.after(60, proximo_nivel)
app.mainloop()

print("\n" + "=" * 58)
if falhas:
    print("FALHAS (%d):" % len(falhas))
    for f in falhas:
        print("  - " + f)
    sys.exit(1)
print("Todos os testes passaram.")
