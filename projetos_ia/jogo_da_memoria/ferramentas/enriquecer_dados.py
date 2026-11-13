# -*- coding: utf-8 -*-
"""Acrescenta a curiosidade de cada constelação ao constelacoes.json e aponta
o campo 'imagem' para as cartas de 400px (as que vão dentro do executável).

Utilitário de build: roda uma vez, não faz parte do jogo.
"""
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON = os.path.join(RAIZ, "constelacoes.json")

CURIOSIDADES = {
    "andromeda": "Abriga a Galáxia de Andrômeda (M31), a galáxia grande mais próxima da nossa e o objeto mais distante visível a olho nu. Na mitologia, é a princesa acorrentada salva por Perseu.",
    "aquarius": "Constelação do zodíaco, representa um jovem derramando água de um jarro. Nela fica a Nebulosa Helix, uma das nebulosas planetárias mais próximas.",
    "aquila": "Sua estrela mais brilhante é Altair, um dos vértices do Triângulo de Verão. Era a águia que carregava os raios de Zeus.",
    "aries": "Constelação do zodíaco que representa o carneiro do velo de ouro. Suas estrelas são fracas; a principal é Hamal.",
    "auriga": "Tem Capela, uma das estrelas mais brilhantes do céu do norte. Suas estrelas formam um pentágono atravessado pela Via Láctea.",
    "bootes": "Contém Arcturus, gigante alaranjada e a estrela mais brilhante do hemisfério celeste norte. Seu desenho lembra uma pipa.",
    "cancer": "A mais apagada do zodíaco. Guarda o aglomerado do Presépio (M44), que a olho nu parece uma manchinha nebulosa.",
    "canis-major": "Tem Sirius, a estrela mais brilhante de todo o céu noturno. É um dos cães de caça que seguem Órion.",
    "canis-minor": "Pequena, formada praticamente por duas estrelas, sendo Prócion a principal. É o segundo cão de Órion.",
    "capricornus": "Representa uma cabra com cauda de peixe. É uma das constelações mais antigas registradas e deu nome ao Trópico de Capricórnio.",
    "carina": "Era parte do antigo navio Argo. Tem Canopus, a segunda estrela mais brilhante do céu, e a enorme Nebulosa da Carina.",
    "cassiopeia": "Fácil de achar pelo W (ou M) formado por cinco estrelas. Era a rainha vaidosa, mãe de Andrômeda.",
    "centaurus": "Abriga Alfa Centauri, o sistema estelar mais próximo do Sol, e Ômega Centauri, o maior aglomerado globular da nossa galáxia.",
    "cepheus": "O rei da Etiópia, marido de Cassiopeia. Sua estrela Delta Cephei deu nome às cefeidas, usadas para medir distâncias no Universo.",
    "cetus": "Uma das maiores constelações do céu. Contém Mira, estrela variável cujo brilho muda bastante ao longo de meses.",
    "corona-borealis": "Um semicírculo de estrelas que lembra uma coroa. Seria a coroa de Ariadne, lançada ao céu por Dionísio.",
    "corvus": "Pequeno quadrilátero bem visível do Brasil. Na mitologia, é o corvo enviado por Apolo que se atrasou e acabou castigado.",
    "crux": "A menor das 88 constelações. Está na bandeira do Brasil e seu braço maior aponta para o polo sul celeste.",
    "cygnus": "Também chamada de Cruz do Norte. Sua estrela Deneb forma o Triângulo de Verão, e a Via Láctea a atravessa.",
    "delphinus": "Pequena e charmosa: quatro estrelas em losango mais uma na cauda. É o golfinho que salvou o músico Aríon.",
    "draco": "Longa e sinuosa, serpenteia entre as duas Ursas. Sua estrela Thuban era a estrela polar na época das pirâmides do Egito.",
    "gemini": "Marcada por Castor e Pólux, as cabeças dos gêmeos. Constelação do zodíaco, bem visível no verão brasileiro.",
    "hercules": "Contém M13, o aglomerado globular mais brilhante do céu do norte. Quatro estrelas centrais formam a figura da Pedra Angular.",
    "leo": "A parte da frente desenha uma foice, e a estrela principal é Regulus. Dela parece vir a chuva de meteoros das Leônidas.",
    "lepus": "Fica logo abaixo dos pés de Órion, como se estivesse fugindo dos cães de caça do caçador.",
    "libra": "Única constelação do zodíaco que representa um objeto, e não um ser vivo. Suas estrelas já foram consideradas as garras do Escorpião.",
    "lyra": "Pequena, mas tem Vega, uma das estrelas mais brilhantes do céu. Abriga a Nebulosa do Anel (M57).",
    "orion": "A mais reconhecível do céu. Tem as Três Marias no cinturão, as supergigantes Betelgeuse e Rigel e a Nebulosa de Órion (M42).",
    "pavo": "Constelação do céu do Sul, criada por navegadores no fim do século XVI. Sua estrela principal é conhecida como Peacock.",
    "pegasus": "Reconhecida pelo Quadrado de Pégaso, quatro estrelas formando um grande quadrilátero. É o cavalo alado da mitologia.",
    "perseus": "O herói que venceu a Medusa. Sua estrela Algol é variável, apelidada de olho do demônio. Dela vem a chuva das Perseidas.",
    "phoenix": "Constelação do céu do Sul que representa a ave que renasce das cinzas. Foi criada por navegadores holandeses.",
    "pisces": "Dois peixes ligados por uma fita. Nela fica o ponto vernal, referência para o sistema de coordenadas do céu.",
    "sagittarius": "Aponta para o centro da nossa galáxia. Suas estrelas centrais desenham a figura de um bule de chá.",
    "scorpius": "Uma das mais fáceis de reconhecer, pela longa cauda curva. Seu coração é Antares, uma supergigante vermelha.",
    "taurus": "Tem o aglomerado das Plêiades (as Sete Estrelas) e as Híades, além da gigante alaranjada Aldebarã.",
    "tucana": "Constelação do céu do Sul. Abriga a Pequena Nuvem de Magalhães e o belo aglomerado globular 47 Tucanae.",
    "ursa-major": "Contém as sete estrelas da Grande Carroça. As duas estrelas da ponta apontam direto para a Estrela Polar.",
    "ursa-minor": "Na ponta da cauda está Polaris, a Estrela do Norte, que marca o polo norte celeste. Não é visível da maior parte do Brasil.",
    "virgo": "A segunda maior constelação do céu. Tem a estrela Spica e o aglomerado de galáxias de Virgem, com mais de mil galáxias.",
}


def main():
    with io.open(JSON, encoding="utf-8") as f:
        dados = json.load(f)

    faltando = [c["id"] for c in dados if c["id"] not in CURIOSIDADES]
    if faltando:
        raise SystemExit("sem curiosidade para: %s" % ", ".join(faltando))

    for c in dados:
        c["imagem"] = "imagens/cartas/%s.jpg" % c["id"]
        c["imagemOriginal"] = "imagens/constelacoes/%s.jpg" % c["id"]
        c["curiosidade"] = CURIOSIDADES[c["id"]]

    with io.open(JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("%d constelações com curiosidade e caminho de carta." % len(dados))


if __name__ == "__main__":
    main()
