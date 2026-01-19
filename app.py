from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *

# Configurações do Jogo
FPS = 30
LARGURA_DA_TELA = 288
ALTURA_DA_TELA = 512
ESPACO_TUBO = 100 
BASE_Y = ALTURA_DA_TELA * 0.79

IMAGENS, SONS, MASCARAS_COLISAO = {}, {}, {}

# Lista de todos os mocergos possíveis
LISTA_JOGADORES = (
    # morcego vermelho
    (
        'assets/img/morcego-asa-fechada.png',
        'assets/img/morcego-asa-aberta.png',
        'assets/img/morcego-asa-fechada.png',
    ),
    # morcego azul
    (
         'assets/img/morcego-asa-fechada.png',
        'assets/img/morcego-asa-aberta.png',
        'assets/img/morcego-asa-fechada.png',
    ),
    # morcego amarelo
    (
         'assets/img/morcego-asa-fechada.png',
        'assets/img/morcego-asa-aberta.png',
        'assets/img/morcego-asa-fechada.png',
    ),
)

# Lista de fundos
LISTA_FUNDOS = (
    'assets/img/fundo1.png',
    'assets/img/fundo1.png',
)

# Lista de canos
LISTA_CANOS = (
    'assets/img/cano-verde.png',
    'assets/img/cano-vermelho.png',
)

# Compatibilidade entre Python 2 e 3
try:
    xrange
except NameError:
    xrange = range


def main():
    global TELA, RELOGIO_FPS
    pygame.init()
    RELOGIO_FPS = pygame.time.Clock()
    TELA = pygame.display.set_mode((LARGURA_DA_TELA, ALTURA_DA_TELA))
    pygame.display.set_caption('Morcegao Caotico')

    # img de números para exibição de pontuação
    IMAGENS['numeros'] = (
        pygame.image.load('assets/img/0.png').convert_alpha(),
        pygame.image.load('assets/img/1.png').convert_alpha(),
        pygame.image.load('assets/img/2.png').convert_alpha(),
        pygame.image.load('assets/img/3.png').convert_alpha(),
        pygame.image.load('assets/img/4.png').convert_alpha(),
        pygame.image.load('assets/img/5.png').convert_alpha(),
        pygame.image.load('assets/img/6.png').convert_alpha(),
        pygame.image.load('assets/img/7.png').convert_alpha(),
        pygame.image.load('assets/img/8.png').convert_alpha(),
        pygame.image.load('assets/img/9.png').convert_alpha()
    )

    # tela de game over
    IMAGENS['gameover'] = pygame.image.load('assets/img/gameover.png').convert_alpha()
    # tela de mensagem para tela de boas-vindas
    IMAGENS['mensagem'] = pygame.image.load('assets/img/message.png').convert_alpha()
    # tela de base (chão)
    IMAGENS['base'] = pygame.image.load('assets/img/base.png').convert_alpha()

    # Sons
    if 'win' in sys.platform:
        extensao_som = '.wav'
    else:
        extensao_som = '.ogg'

    SONS['morrer'] = pygame.mixer.Sound('assets/audio/die' + extensao_som)
    SONS['bater']  = pygame.mixer.Sound('assets/audio/hit' + extensao_som)
    SONS['ponto']  = pygame.mixer.Sound('assets/audio/point' + extensao_som)
    SONS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + extensao_som)
    SONS['asa']    = pygame.mixer.Sound('assets/audio/wing' + extensao_som)

    while True:
        # Seleciona img de fundo aleatório
        indice_fundo = random.randint(0, len(LISTA_FUNDOS) - 1)
        IMAGENS['fundo'] = pygame.image.load(LISTA_FUNDOS[indice_fundo]).convert()

        # Seleciona img aleatórios do morcego
        indice_jogador = random.randint(0, len(LISTA_JOGADORES) - 1)
        IMAGENS['jogador'] = (
            pygame.image.load(LISTA_JOGADORES[indice_jogador][0]).convert_alpha(),
            pygame.image.load(LISTA_JOGADORES[indice_jogador][1]).convert_alpha(),
            pygame.image.load(LISTA_JOGADORES[indice_jogador][2]).convert_alpha(),
        )

        # Seleciona img aleatórios de canos
        indice_cano = random.randint(0, len(LISTA_CANOS) - 1)
        IMAGENS['cano'] = (
            pygame.transform.flip(
                pygame.image.load(LISTA_CANOS[indice_cano]).convert_alpha(), False, True),
            pygame.image.load(LISTA_CANOS[indice_cano]).convert_alpha(),
        )

        # Máscara de colisão para canos
        MASCARAS_COLISAO['cano'] = (
            obter_mascara_colisao(IMAGENS['cano'][0]),
            obter_mascara_colisao(IMAGENS['cano'][1]),
        )

        # Máscara de colisão para o morcego
        MASCARAS_COLISAO['jogador'] = (
            obter_mascara_colisao(IMAGENS['jogador'][0]),
            obter_mascara_colisao(IMAGENS['jogador'][1]),
            obter_mascara_colisao(IMAGENS['jogador'][2]),
        )

        info_movimento = mostrar_animacao_bem_vindo()
        info_colisao = jogo_principal(info_movimento)
        mostrar_tela_game_over(info_colisao)


def mostrar_animacao_bem_vindo():
    indice_jogador = 0
    gerador_indice_jogador = cycle([0, 1, 2, 1])
    # Iterador usado para mudar o índice do morcego a cada 5ª iteração
    iteracao_loop = 0

    posicao_passaro_x = int(LARGURA_DA_TELA * 0.2)
    posicao_passaro_y = int((ALTURA_DA_TELA - IMAGENS['jogador'][0].get_height()) / 2)

    mensagem_x = int((LARGURA_DA_TELA - IMAGENS['mensagem'].get_width()) / 2)
    mensagem_y = int(ALTURA_DA_TELA * 0.12)

    base_x = 0
    # Quantidade máxima que a base pode se deslocar para a esquerda
    deslocamento_base = IMAGENS['base'].get_width() - IMAGENS['fundo'].get_width()

    # Tremulação do morcego para movimento cima-baixo na tela de boas-vindas
    valores_tremulacao = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # Toca som de batida de asa e retorna valores para jogo_principal
                SONS['asa'].play()
                return {
                    'y_jogador': posicao_passaro_y + valores_tremulacao['val'],
                    'x_base': base_x,
                    'gerador_indice_jogador': gerador_indice_jogador,
                }

        # Ajusta posição do morcego, índice do morcego e posição da base
        if (iteracao_loop + 1) % 5 == 0:
            indice_jogador = next(gerador_indice_jogador)
        iteracao_loop = (iteracao_loop + 1) % 30
        base_x = -((-base_x + 4) % deslocamento_base)
        tremulacao_jogador(valores_tremulacao)

        # Desenha img
        TELA.blit(IMAGENS['fundo'], (0,0))
        TELA.blit(IMAGENS['jogador'][indice_jogador],
                    (posicao_passaro_x, posicao_passaro_y + valores_tremulacao['val']))
        TELA.blit(IMAGENS['mensagem'], (mensagem_x, mensagem_y))
        TELA.blit(IMAGENS['base'], (base_x, BASE_Y))

        pygame.display.update()
        RELOGIO_FPS.tick(FPS)


def jogo_principal(info_movimento):
    pontuacao = indice_jogador = iteracao_loop = 0
    gerador_indice_jogador = info_movimento['gerador_indice_jogador']
    posicao_passaro_x, posicao_passaro_y = int(LARGURA_DA_TELA * 0.2), info_movimento['y_jogador']

    base_x = info_movimento['x_base']
    deslocamento_base = IMAGENS['base'].get_width() - IMAGENS['fundo'].get_width()

    # Obtém 2 novos canos para adicionar às listas de canos
    novo_cano1 = obter_cano_aleatorio()
    novo_cano2 = obter_cano_aleatorio()

    # Lista de canos superiores
    canos_superiores = [
        {'x': LARGURA_DA_TELA + 200, 'y': novo_cano1[0]['y']},
        {'x': LARGURA_DA_TELA + 200 + (LARGURA_DA_TELA / 2), 'y': novo_cano2[0]['y']},
    ]

    # Lista de canos inferiores
    canos_inferiores = [
        {'x': LARGURA_DA_TELA + 200, 'y': novo_cano1[1]['y']},
        {'x': LARGURA_DA_TELA + 200 + (LARGURA_DA_TELA / 2), 'y': novo_cano2[1]['y']},
    ]

    dt = RELOGIO_FPS.tick(FPS)/1000
    velocidade_cano_x = -128 * dt

    # Variáveis de física do morcego
    velocidade_passaro_y     =  -9   # Velocidade do morcego no eixo Y
    velocidade_max_passaro_y =  10   # Velocidade máxima de descida
    velocidade_min_passaro_y =  -8   # Velocidade máxima de subida
    aceleracao_passaro_y     =   1   # Aceleração para baixo (gravidade)
    rotacao_passaro          =  45   # Rotação atual do morcego
    velocidade_rotacao       =   3   # Velocidade angular
    limite_rotacao           =  20   # Limite de rotação visual
    aceleracao_batida_asa    =  -9   # Impulso ao bater asas
    bateu_asa                = False # Estado se o morcego bateu asa


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if posicao_passaro_y > -2 * IMAGENS['jogador'][0].get_height():
                    velocidade_passaro_y = aceleracao_batida_asa
                    bateu_asa = True
                    SONS['asa'].play()

        # Verifica colisão
        teste_colisao = verificar_colisao({'x': posicao_passaro_x, 'y': posicao_passaro_y, 'index': indice_jogador},
                               canos_superiores, canos_inferiores)
        if teste_colisao[0]:
            return {
                'y': posicao_passaro_y,
                'colisao_chao': teste_colisao[1],
                'x_base': base_x,
                'canos_superiores': canos_superiores,
                'canos_inferiores': canos_inferiores,
                'pontuacao': pontuacao,
                'velocidade_y_jogador': velocidade_passaro_y,
                'rotacao_jogador': rotacao_passaro
            }

        # Verifica pontuação
        posicao_centro_passaro = posicao_passaro_x + IMAGENS['jogador'][0].get_width() / 2
        for cano in canos_superiores:
            posicao_centro_cano = cano['x'] + IMAGENS['cano'][0].get_width() / 2
            if posicao_centro_cano <= posicao_centro_passaro < posicao_centro_cano + 4:
                pontuacao += 1
                SONS['ponto'].play()

        # Muda índice do morcego e posição da base
        if (iteracao_loop + 1) % 3 == 0:
            indice_jogador = next(gerador_indice_jogador)
        iteracao_loop = (iteracao_loop + 1) % 30
        base_x = -((-base_x + 100) % deslocamento_base)

        # Rotaciona o morcego
        if rotacao_passaro > -90:
            rotacao_passaro -= velocidade_rotacao

        # Movimento do morcego
        if velocidade_passaro_y < velocidade_max_passaro_y and not bateu_asa:
            velocidade_passaro_y += aceleracao_passaro_y
        if bateu_asa:
            bateu_asa = False
            # Mais rotação para cobrir o limite (visual)
            rotacao_passaro = 45

        altura_passaro = IMAGENS['jogador'][indice_jogador].get_height()
        posicao_passaro_y += min(velocidade_passaro_y, BASE_Y - posicao_passaro_y - altura_passaro)

        # Move canos para a esquerda
        for cano_sup, cano_inf in zip(canos_superiores, canos_inferiores):
            cano_sup['x'] += velocidade_cano_x
            cano_inf['x'] += velocidade_cano_x

        # Adiciona novo cano quando o primeiro está prestes a sair da tela
        if 3 > len(canos_superiores) > 0 and 0 < canos_superiores[0]['x'] < 5:
            novo_cano = obter_cano_aleatorio()
            canos_superiores.append(novo_cano[0])
            canos_inferiores.append(novo_cano[1])

        # Remove primeiro cano se saiu da tela
        if len(canos_superiores) > 0 and canos_superiores[0]['x'] < -IMAGENS['cano'][0].get_width():
            canos_superiores.pop(0)
            canos_inferiores.pop(0)

        # Desenha img
        TELA.blit(IMAGENS['fundo'], (0,0))

        for cano_sup, cano_inf in zip(canos_superiores, canos_inferiores):
            TELA.blit(IMAGENS['cano'][0], (cano_sup['x'], cano_sup['y']))
            TELA.blit(IMAGENS['cano'][1], (cano_inf['x'], cano_inf['y']))

        TELA.blit(IMAGENS['base'], (base_x, BASE_Y))
        
        # Exibe pontuação
        mostrar_pontuacao(pontuacao)

        # Rotação visível do morcego tem um limite
        rotacao_visivel = limite_rotacao
        if rotacao_passaro <= limite_rotacao:
            rotacao_visivel = rotacao_passaro
        
        superficie_passaro = pygame.transform.rotate(IMAGENS['jogador'][indice_jogador], rotacao_visivel)
        TELA.blit(superficie_passaro, (posicao_passaro_x, posicao_passaro_y))

        pygame.display.update()
        RELOGIO_FPS.tick(FPS)


def mostrar_tela_game_over(info_colisao):
    pontuacao = info_colisao['pontuacao']
    posicao_passaro_x = LARGURA_DA_TELA * 0.2
    posicao_passaro_y = info_colisao['y']
    altura_passaro = IMAGENS['jogador'][0].get_height()
    velocidade_passaro_y = info_colisao['velocidade_y_jogador']
    aceleracao_passaro_y = 2
    rotacao_passaro = info_colisao['rotacao_jogador']
    velocidade_rotacao = 7

    base_x = info_colisao['x_base']

    canos_superiores = info_colisao['canos_superiores']
    canos_inferiores = info_colisao['canos_inferiores']

    # Toca sons de batida e morte
    SONS['bater'].play()
    if not info_colisao['colisao_chao']:
        SONS['morrer'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if posicao_passaro_y + altura_passaro >= BASE_Y - 1:
                    return

        # Deslocamento vertical do morcego (caindo)
        if posicao_passaro_y + altura_passaro < BASE_Y - 1:
            posicao_passaro_y += min(velocidade_passaro_y, BASE_Y - posicao_passaro_y - altura_passaro)

        # Muda a velocidade do morcego
        if velocidade_passaro_y < 15:
            velocidade_passaro_y += aceleracao_passaro_y

        # Rotaciona apenas quando não colidiu com o chão (cai de bico)
        if not info_colisao['colisao_chao']:
            if rotacao_passaro > -90:
                rotacao_passaro -= velocidade_rotacao

        # Desenha img
        TELA.blit(IMAGENS['fundo'], (0,0))

        for cano_sup, cano_inf in zip(canos_superiores, canos_inferiores):
            TELA.blit(IMAGENS['cano'][0], (cano_sup['x'], cano_sup['y']))
            TELA.blit(IMAGENS['cano'][1], (cano_inf['x'], cano_inf['y']))

        TELA.blit(IMAGENS['base'], (base_x, BASE_Y))
        mostrar_pontuacao(pontuacao)

        superficie_passaro = pygame.transform.rotate(IMAGENS['jogador'][1], rotacao_passaro)
        TELA.blit(superficie_passaro, (posicao_passaro_x,posicao_passaro_y))
        TELA.blit(IMAGENS['gameover'], (50, 180))

        RELOGIO_FPS.tick(FPS)
        pygame.display.update()


def tremulacao_jogador(tremulacao):
    if abs(tremulacao['val']) == 8:
        tremulacao['dir'] *= -1

    if tremulacao['dir'] == 1:
         tremulacao['val'] += 1
    else:
        tremulacao['val'] -= 1


def obter_cano_aleatorio():
    posicao_gap_y = random.randrange(0, int(BASE_Y * 0.6 - ESPACO_TUBO))
    posicao_gap_y += int(BASE_Y * 0.2)
    altura_cano = IMAGENS['cano'][0].get_height()
    posicao_cano_x = LARGURA_DA_TELA + 10

    return [
        {'x': posicao_cano_x, 'y': posicao_gap_y - altura_cano},  # cano superior
        {'x': posicao_cano_x, 'y': posicao_gap_y + ESPACO_TUBO},  # cano inferior
    ]


def mostrar_pontuacao(pontuacao):
    digitos = [int(x) for x in list(str(pontuacao))]
    largura_total = 0 # Largura total de todos os números a serem impressos

    for digito in digitos:
        largura_total += IMAGENS['numeros'][digito].get_width()

    deslocamento_x = (LARGURA_DA_TELA - largura_total) / 2

    for digito in digitos:
        TELA.blit(IMAGENS['numeros'][digito], (deslocamento_x, ALTURA_DA_TELA * 0.1))
        deslocamento_x += IMAGENS['numeros'][digito].get_width()


def verificar_colisao(jogador, canos_superiores, canos_inferiores):
    """Retorna True se o morcego colide com a base ou canos."""
    indice_jogador = jogador['index']
    jogador['w'] = IMAGENS['jogador'][0].get_width()
    jogador['h'] = IMAGENS['jogador'][0].get_height()

    # Se o morcego colide com o chão
    if jogador['y'] + jogador['h'] >= BASE_Y - 1:
        return [True, True]
    else:

        retangulo_jogador = pygame.Rect(jogador['x'], jogador['y'],
                      jogador['w'], jogador['h'])
        largura_cano = IMAGENS['cano'][0].get_width()
        altura_cano = IMAGENS['cano'][0].get_height()

        for cano_sup, cano_inf in zip(canos_superiores, canos_inferiores):
            # Retângulos de canos superior e inferior
            retangulo_cano_sup = pygame.Rect(cano_sup['x'], cano_sup['y'], largura_cano, altura_cano)
            retangulo_cano_inf = pygame.Rect(cano_inf['x'], cano_inf['y'], largura_cano, altura_cano)

            # Máscaras de colisão do morcego e canos
            mascara_colisao_jogador = MASCARAS_COLISAO['jogador'][indice_jogador]
            mascara_colisao_cano_sup = MASCARAS_COLISAO['cano'][0]
            mascara_colisao_cano_inf = MASCARAS_COLISAO['cano'][1]

            # Verifica se colidiu
            colisao_superior = colisao_pixel(retangulo_jogador, retangulo_cano_sup, mascara_colisao_jogador, mascara_colisao_cano_sup)
            colisao_inferior = colisao_pixel(retangulo_jogador, retangulo_cano_inf, mascara_colisao_jogador, mascara_colisao_cano_inf)

            if colisao_superior or colisao_inferior:
                return [True, False]

    return [False, False]

def colisao_pixel(ret1, ret2, mascara1, mascara2):
    ret = ret1.clip(ret2)

    if ret.width == 0 or ret.height == 0:
        return False

    x1, y1 = ret.x - ret1.x, ret.y - ret1.y
    x2, y2 = ret.x - ret2.x, ret.y - ret2.y

    for x in xrange(ret.width):
        for y in xrange(ret.height):
            if mascara1[x1+x][y1+y] and mascara2[x2+x][y2+y]:
                return True
    return False

def obter_mascara_colisao(imagem):
    mascara = []
    for x in xrange(imagem.get_width()):
        mascara.append([])
        for y in xrange(imagem.get_height()):
            mascara[x].append(bool(imagem.get_at((x,y))[3]))
    return mascara

if __name__ == '__main__':
    main()