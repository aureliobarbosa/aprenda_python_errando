import pygame
import time
# import random

# Inicializa o pygame
pygame.init()

# Definindo cores
branco = (255, 255, 255) # tuple (tupla em português)
preto = (0, 0, 0)
vermelho = (213, 50, 80)
verde = (0, 255, 0)
azul = (50, 153, 213)

print('vermelho: \n', vermelho[0],vermelho[1], vermelho[2])

# Tamanho da tela
largura_tela = 1200
altura_tela = 400

# Inicializa a tela
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption('Jogo da Cobrinha para Iniciantes')

# Relógio para controlar a velocidade do jogo
relogio = pygame.time.Clock()

# Tamanho do bloco da cobra e velocidade
tamanho_bloco = 20
velocidade_cobra = 15

# Fontes para mensagens
fonte_estilo = pygame.font.SysFont("bahnschrift", 25)
fonte_pontuacao = pygame.font.SysFont("comicsansms", 35)

def mostra_pontuacao(pontuacao):
    valor = fonte_pontuacao.render("Sua Pontuação: " + str(pontuacao), True, vermelho)
    tela.blit(valor, [0, 0])

def desenha_cobra(tamanho_bloco, lista_cobra):
    for bloco in lista_cobra:
        pygame.draw.rect(tela, verde, [bloco[0], bloco[1], tamanho_bloco, tamanho_bloco])

def mensagem(msg, cor):
    mensagem = fonte_estilo.render(msg, True, cor)
    tela.blit(mensagem, [largura_tela / 6, altura_tela / 3])

def jogo():
    game_over = False
    game_close = False

    # Posição inicial da cobra
    x1 = largura_tela / 2
    y1 = altura_tela / 2

    # Mudança de posição
    x1_mudanca = 0
    y1_mudanca = 0

    # Corpo da cobra (lista de segmentos)
    lista_cobra = []
    comprimento_cobra = 1

    # Posição da comida
    comida_x = ((largura_tela - tamanho_bloco) / 20.0) * 20.0
    comida_y = ((altura_tela - tamanho_bloco) / 20.0) * 20.0

    while not game_over:

        while game_close == True:
            tela.fill(branco)
            mensagem("Você Perdeu! Pressione Q-Sair ou C-Jogar Novamente", vermelho)
            mostra_pontuacao(comprimento_cobra - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        jogo()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_mudanca = -tamanho_bloco
                    y1_mudanca = 0
                elif event.key == pygame.K_RIGHT:
                    x1_mudanca = tamanho_bloco
                    y1_mudanca = 0
                elif event.key == pygame.K_UP:
                    y1_mudanca = -tamanho_bloco
                    x1_mudanca = 0
                elif event.key == pygame.K_DOWN:
                    y1_mudanca = tamanho_bloco
                    x1_mudanca = 0

        # Verifica se a cobra bateu na borda
        if x1 >= largura_tela or x1 < 0 or y1 >= altura_tela or y1 < 0:
            game_close = True

        # Atualiza a posição da cobra
        x1 += x1_mudanca
        y1 += y1_mudanca
        tela.fill(preto)
        
        # Desenha a comida
        pygame.draw.rect(tela, azul, [comida_x, comida_y, tamanho_bloco, tamanho_bloco])
        
        # Atualiza a cabeça da cobra
        cabeca_cobra = []
        cabeca_cobra.append(x1)
        cabeca_cobra.append(y1)
        lista_cobra.append(cabeca_cobra)
        
        # Remove segmentos extras se a cobra não cresceu
        if len(lista_cobra) > comprimento_cobra:
            del lista_cobra[0]

        # Verifica se a cobra bateu em si mesma
        for segmento in lista_cobra[:-1]:
            if segmento == cabeca_cobra:
                game_close = True

        # Desenha a cobra
        desenha_cobra(tamanho_bloco, lista_cobra)
        mostra_pontuacao(comprimento_cobra - 1)

        pygame.display.update()

        # Verifica se a cobra comeu a comida
        if x1 == comida_x and y1 == comida_y:
            comida_x = round(random.randrange(0, largura_tela - tamanho_bloco) / 20.0) * 20.0
            comida_y = round(random.randrange(0, altura_tela - tamanho_bloco) / 20.0) * 20.0
            comprimento_cobra += 1

        relogio.tick(velocidade_cobra)

    pygame.quit()
    quit()

# Inicia o jogo
jogo()