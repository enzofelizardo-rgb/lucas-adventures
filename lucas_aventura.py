import pygame
import sys
import random
import math

# ==================== CONFIGURAÇÕES ====================
pygame.init()
LARGURA, ALTURA = 1000, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Lucas - Aventura dos 4 Mundos")
CLOCK = pygame.time.Clock()
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AZUL = (70, 130, 180)
MARROM = (139, 69, 19)
CINZA = (100, 100, 100)
AMARELO = (255, 215, 0)
ROXO = (128, 0, 128)
VERMELHO = (220, 20, 60)
LARANJA = (255, 140, 0)
CIANO = (0, 255, 255)

# ==================== FONTES ====================
fonte = pygame.font.SysFont("Arial", 24)
fonte_grande = pygame.font.SysFont("Arial", 48, bold=True)
fonte_media = pygame.font.SysFont("Arial", 32)

# ==================== CLASSES ====================

class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.vel_x = 0
        self.vel_y = 0
        self.velocidade = 6
        self.pulo = -15
        self.gravidade = 0.7
        self.no_chao = False
        self.vida = 100
        self.vida_max = 100
        self.ataque = False
        self.ataque_cooldown = 0
        self.direcao = 1  # 1 = direita, -1 = esquerda
        self.invencivel = 0
        self.chaves = 0
        self.itens_especiais = 0
        self.dano = 25

    def atualizar(self, plataformas):
        # Movimento
        teclas = pygame.key.get_pressed()
        self.vel_x = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x = -self.velocidade
            self.direcao = -1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x = self.velocidade
            self.direcao = 1
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_w] or teclas[pygame.K_UP]) and self.no_chao:
            self.vel_y = self.pulo
            self.no_chao = False

        # Ataque com espada
        if teclas[pygame.K_j] or teclas[pygame.K_z]:
            if self.ataque_cooldown <= 0:
                self.ataque = True
                self.ataque_cooldown = 20

        if self.ataque_cooldown > 0:
            self.ataque_cooldown -= 1
        else:
            self.ataque = False

        # Física
        self.vel_y += self.gravidade
        self.rect.x += self.vel_x
        self.colisao_x(plataformas)
        self.rect.y += self.vel_y
        self.no_chao = False
        self.colisao_y(plataformas)

        # Limites da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LARGURA:
            self.rect.right = LARGURA
        if self.rect.top > ALTURA:
            self.vida = 0  # Caiu no vazio

        if self.invencivel > 0:
            self.invencivel -= 1

    def colisao_x(self, plataformas):
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_x > 0:
                    self.rect.right = p.left
                elif self.vel_x < 0:
                    self.rect.left = p.right

    def colisao_y(self, plataformas):
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

    def get_espada_rect(self):
        if self.ataque:
            if self.direcao == 1:
                return pygame.Rect(self.rect.right, self.rect.centery - 10, 50, 20)
            else:
                return pygame.Rect(self.rect.left - 50, self.rect.centery - 10, 50, 20)
        return pygame.Rect(0, 0, 0, 0)

    def tomar_dano(self, quantidade):
        if self.invencivel <= 0:
            self.vida -= quantidade
            self.invencivel = 60  # 1 segundo de invencibilidade
            if self.vida < 0:
                self.vida = 0

    def desenhar(self, tela):
        # Corpo do Lucas
        cor = (0, 150, 255) if self.invencivel % 10 < 5 or self.invencivel <= 0 else (100, 100, 255)
        pygame.draw.rect(tela, cor, self.rect)
        # Cabeça
        pygame.draw.circle(tela, (255, 220, 180), (self.rect.centerx, self.rect.top + 12), 12)
        # Olhos
        olho_x = self.rect.centerx + (5 * self.direcao)
        pygame.draw.circle(tela, PRETO, (olho_x, self.rect.top + 10), 3)
        # Espada
        if self.ataque:
            espada = self.get_espada_rect()
            pygame.draw.rect(tela, CINZA, espada)
            pygame.draw.rect(tela, AMARELO, espada, 2)

class Inimigo:
    def __init__(self, x, y, vida=50, velocidade=2, tipo="normal"):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.vida = vida
        self.vida_max = vida
        self.velocidade = velocidade
        self.direcao = 1
        self.tipo = tipo
        self.contador = 0
        self.vivo = True
        self.dano = 15 if tipo != "chefe" else 25

    def atualizar(self, plataformas, jogador):
        if not self.vivo:
            return

        self.contador += 1

        if self.tipo == "chefe":
            # Chefe persegue o jogador
            if jogador.rect.centerx > self.rect.centerx:
                self.direcao = 1
            else:
                self.direcao = -1
            self.rect.x += self.velocidade * self.direcao
        else:
            # Patrulha simples
            if self.contador % 120 == 0:
                self.direcao *= -1
            self.rect.x += self.velocidade * self.direcao

        # Gravidade simples
        self.rect.y += 5
        for p in plataformas:
            if self.rect.colliderect(p):
                self.rect.bottom = p.top

        # Colisão com jogador
        if self.rect.colliderect(jogador.rect) and jogador.invencivel <= 0:
            jogador.tomar_dano(self.dano)

    def tomar_dano(self, quantidade):
        self.vida -= quantidade
        if self.vida <= 0:
            self.vivo = False

    def desenhar(self, tela):
        if not self.vivo:
            return
        if self.tipo == "chefe":
            cor = ROXO
            # Barra de vida do chefe
            pygame.draw.rect(tela, VERMELHO, (self.rect.x - 30, self.rect.y - 25, 100, 12))
            vida_pct = max(0, self.vida / self.vida_max)
            pygame.draw.rect(tela, (0, 255, 0), (self.rect.x - 30, self.rect.y - 25, 100 * vida_pct, 12))
            pygame.draw.rect(tela, BRANCO, (self.rect.x - 30, self.rect.y - 25, 100, 12), 2)
        else:
            cor = VERMELHO

        pygame.draw.rect(tela, cor, self.rect)
        # Olhos
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx - 8, self.rect.top + 15), 6)
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx + 8, self.rect.top + 15), 6)
        pygame.draw.circle(tela, PRETO, (self.rect.centerx - 8, self.rect.top + 15), 3)
        pygame.draw.circle(tela, PRETO, (self.rect.centerx + 8, self.rect.top + 15), 3)

class Item:
    def __init__(self, x, y, tipo="chave"):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.tipo = tipo  # "chave" ou "especial"
        self.coletado = False
        self.angulo = 0

    def atualizar(self):
        self.angulo += 3

    def desenhar(self, tela):
        if self.coletado:
            return
        if self.tipo == "chave":
            # Chave dourada
            pygame.draw.circle(tela, AMARELO, (self.rect.centerx, self.rect.centery), 12)
            pygame.draw.rect(tela, AMARELO, (self.rect.centerx - 4, self.rect.centery, 8, 18))
            pygame.draw.rect(tela, (200, 150, 0), (self.rect.centerx + 4, self.rect.centery + 8, 8, 4))
        else:
            # Item especial (estrela)
            pontos = []
            for i in range(5):
                ang = math.radians(self.angulo + i * 72)
                pontos.append((self.rect.centerx + 15 * math.cos(ang),
                               self.rect.centery + 15 * math.sin(ang)))
            pygame.draw.polygon(tela, CIANO, pontos)

class Mundo:
    def __init__(self, nome, cor_fundo, plataformas, inimigos, itens, chave_pos, portal_pos=None):
        self.nome = nome
        self.cor_fundo = cor_fundo
        self.plataformas = plataformas
        self.inimigos = inimigos
        self.itens = itens
        self.chave = Item(chave_pos[0], chave_pos[1], "chave")
        self.portal = portal_pos  # (x, y) do portal no último mundo
        self.portal_fechado = False

# ==================== CRIAÇÃO DOS MUNDOS ====================

def criar_mundos():
    mundos = []

    # ===== 1. FLORESTA ENCANTADA =====
    plataformas1 = [
        pygame.Rect(0, 550, 1000, 50),
        pygame.Rect(150, 450, 150, 20),
        pygame.Rect(400, 380, 120, 20),
        pygame.Rect(600, 300, 150, 20),
        pygame.Rect(800, 420, 120, 20),
        pygame.Rect(50, 300, 100, 20),
    ]
    inimigos1 = [
        Inimigo(200, 400, 40, 2),
        Inimigo(450, 330, 40, 2),
        Inimigo(650, 250, 50, 2.5),
    ]
    itens1 = [
        Item(180, 410, "especial"),
        Item(620, 260, "especial"),
    ]
    mundos.append(Mundo("Floresta Encantada", (20, 80, 40), plataformas1, inimigos1, itens1, (820, 380)))

    # ===== 2. CIDADE PRINCIPAL =====
    plataformas2 = [
        pygame.Rect(0, 550, 1000, 50),
        pygame.Rect(100, 470, 100, 20),
        pygame.Rect(250, 400, 100, 20),
        pygame.Rect(400, 330, 100, 20),
        pygame.Rect(550, 400, 100, 20),
        pygame.Rect(700, 470, 100, 20),
        pygame.Rect(850, 350, 120, 20),
        pygame.Rect(50, 250, 80, 20),
    ]
    inimigos2 = [
        Inimigo(120, 420, 50, 2.5),
        Inimigo(420, 280, 50, 2.5),
        Inimigo(720, 420, 60, 3),
        Inimigo(880, 300, 50, 2),
    ]
    itens2 = [
        Item(270, 360, "especial"),
        Item(870, 310, "especial"),
    ]
    mundos.append(Mundo("Cidade Principal", (40, 40, 80), plataformas2, inimigos2, itens2, (870, 310)))

    # ===== 3. CASTELO ABANDONADO =====
    plataformas3 = [
        pygame.Rect(0, 550, 1000, 50),
        pygame.Rect(80, 480, 80, 20),
        pygame.Rect(200, 400, 100, 20),
        pygame.Rect(350, 320, 80, 20),
        pygame.Rect(500, 250, 100, 20),
        pygame.Rect(650, 320, 80, 20),
        pygame.Rect(780, 400, 100, 20),
        pygame.Rect(900, 480, 80, 20),
        pygame.Rect(300, 180, 120, 20),
    ]
    inimigos3 = [
        Inimigo(220, 350, 70, 2.5),
        Inimigo(520, 200, 80, 3),
        Inimigo(800, 350, 70, 2.5),
        Inimigo(320, 130, 60, 2),
    ]
    itens3 = [
        Item(360, 280, "especial"),
        Item(520, 210, "especial"),
        Item(320, 140, "especial"),
    ]
    mundos.append(Mundo("Castelo Abandonado", (50, 30, 30), plataformas3, inimigos3, itens3, (920, 440)))

    # ===== 4. PORTAL MÁGICO (com chefe) =====
    plataformas4 = [
        pygame.Rect(0, 550, 1000, 50),
        pygame.Rect(150, 450, 120, 20),
        pygame.Rect(400, 380, 200, 20),
        pygame.Rect(700, 450, 120, 20),
        pygame.Rect(300, 280, 100, 20),
        pygame.Rect(550, 280, 100, 20),
    ]
    # Guardião do Portal - 1000 de vida
    chefe = Inimigo(450, 300, 1000, 1.5, "chefe")
    inimigos4 = [chefe]
    itens4 = [
        Item(180, 410, "especial"),
        Item(730, 410, "especial"),
    ]
    mundos.append(Mundo("Portal Mágico", (30, 0, 50), plataformas4, inimigos4, itens4, (480, 330), (480, 200)))

    return mundos

# ==================== FUNÇÕES AUXILIARES ====================

def desenhar_hud(jogador, mundo_atual, total_mundos):
    # Vida
    pygame.draw.rect(TELA, VERMELHO, (20, 20, 200, 20))
    vida_pct = jogador.vida / jogador.vida_max
    pygame.draw.rect(TELA, (0, 200, 0), (20, 20, 200 * vida_pct, 20))
    pygame.draw.rect(TELA, BRANCO, (20, 20, 200, 20), 2)
    texto_vida = fonte.render(f"Vida: {jogador.vida}", True, BRANCO)
    TELA.blit(texto_vida, (25, 18))

    # Chaves
    texto_chaves = fonte.render(f"Chaves: {jogador.chaves}/4", True, AMARELO)
    TELA.blit(texto_chaves, (20, 50))

    # Itens especiais
    texto_itens = fonte.render(f"Itens Especiais: {jogador.itens_especiais}", True, CIANO)
    TELA.blit(texto_itens, (20, 80))

    # Mundo atual
    texto_mundo = fonte.render(f"Mundo: {mundo_atual.nome}", True, BRANCO)
    TELA.blit(texto_mundo, (LARGURA - 300, 20))

    # Controles
    controles = fonte.render("A/D ou ←/→: Mover | Espaço: Pular | J ou Z: Espada", True, (180, 180, 180))
    TELA.blit(controles, (LARGURA // 2 - 220, ALTURA - 30))

def desenhar_portal(x, y, fechado):
    if fechado:
        # Portal fechado
        pygame.draw.circle(TELA, (50, 50, 50), (x, y), 40)
        pygame.draw.circle(TELA, (100, 100, 100), (x, y), 30)
        texto = fonte.render("FECHADO", True, VERDE)
        TELA.blit(texto, (x - 40, y - 10))
    else:
        # Portal aberto (girando)
        pygame.draw.circle(TELA, ROXO, (x, y), 45)
        pygame.draw.circle(TELA, (180, 0, 255), (x, y), 35)
        pygame.draw.circle(TELA, CIANO, (x, y), 20)
        texto = fonte.render("PORTAL", True, BRANCO)
        TELA.blit(texto, (x - 35, y - 10))

def tela_mensagem(texto, subtexto=""):
    TELA.fill(PRETO)
    t = fonte_grande.render(texto, True, AMARELO)
    TELA.blit(t, (LARGURA // 2 - t.get_width() // 2, ALTURA // 2 - 50))
    if subtexto:
        s = fonte_media.render(subtexto, True, BRANCO)
        TELA.blit(s, (LARGURA // 2 - s.get_width() // 2, ALTURA // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(2500)

# ==================== LOOP PRINCIPAL ====================

def main():
    mundos = criar_mundos()
    mundo_idx = 0
    jogador = Jogador(50, 480)
    estado = "jogando"  # jogando, vitoria, derrota, transicao

    while True:
        CLOCK.tick(FPS)
        mundo = mundos[mundo_idx]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r and estado in ["derrota", "vitoria"]:
                    # Reiniciar
                    mundos = criar_mundos()
                    mundo_idx = 0
                    jogador = Jogador(50, 480)
                    estado = "jogando"

        if estado == "jogando":
            # Atualizar
            jogador.atualizar(mundo.plataformas)

            for inimigo in mundo.inimigos:
                inimigo.atualizar(mundo.plataformas, jogador)

            # Ataque da espada
            if jogador.ataque:
                espada = jogador.get_espada_rect()
                for inimigo in mundo.inimigos:
                    if inimigo.vivo and espada.colliderect(inimigo.rect):
                        inimigo.tomar_dano(jogador.dano)

            # Coletar itens
            for item in mundo.itens:
                if not item.coletado and jogador.rect.colliderect(item.rect):
                    item.coletado = True
                    jogador.itens_especiais += 1
                    jogador.vida = min(jogador.vida_max, jogador.vida + 20)  # cura

            # Coletar chave
            if not mundo.chave.coletado and jogador.rect.colliderect(mundo.chave.rect):
                mundo.chave.coletado = True
                jogador.chaves += 1

            # Verificar se caiu ou morreu
            if jogador.vida <= 0:
                estado = "derrota"

            # Passar de mundo
            if mundo.chave.coletado and jogador.rect.right >= LARGURA - 10:
                if mundo_idx < 3:
                    mundo_idx += 1
                    jogador.rect.x = 50
                    jogador.rect.y = 480
                    jogador.vel_y = 0
                    tela_mensagem(f"Entrando em: {mundos[mundo_idx].nome}", "Continue sua aventura!")
                else:
                    # Último mundo - verificar se matou o chefe e tem 4 chaves
                    chefe_morto = not any(i.vivo for i in mundo.inimigos)
                    if chefe_morto and jogador.chaves >= 4:
                        mundo.portal_fechado = True
                        estado = "vitoria"

            # Atualizar itens animados
            for item in mundo.itens:
                item.atualizar()
            mundo.chave.atualizar()

            # Desenhar
            TELA.fill(mundo.cor_fundo)

            # Plataformas
            for p in mundo.plataformas:
                pygame.draw.rect(TELA, MARROM, p)
                pygame.draw.rect(TELA, (100, 50, 0), p, 2)

            # Portal (só no último mundo)
            if mundo.portal:
                desenhar_portal(mundo.portal[0], mundo.portal[1], mundo.portal_fechado)

            # Itens e chave
            for item in mundo.itens:
                item.desenhar(TELA)
            mundo.chave.desenhar(TELA)

            # Inimigos
            for inimigo in mundo.inimigos:
                inimigo.desenhar(TELA)

            # Jogador
            jogador.desenhar(TELA)

            # HUD
            desenhar_hud(jogador, mundo, len(mundos))

            # Mensagem especial no último mundo
            if mundo_idx == 3:
                if any(i.vivo for i in mundo.inimigos):
                    msg = fonte.render("Derrote o Guardião do Portal (1000 HP)!", True, VERMELHO)
                    TELA.blit(msg, (LARGURA // 2 - 200, 100))
                elif jogador.chaves >= 4:
                    msg = fonte.render("Portal pode ser fechado! Vá até o final da tela!", True, VERDE)
                    TELA.blit(msg, (LARGURA // 2 - 250, 100))

        elif estado == "derrota":
            TELA.fill(PRETO)
            t = fonte_grande.render("VOCÊ MORREU!", True, VERMELHO)
            TELA.blit(t, (LARGURA // 2 - t.get_width() // 2, ALTURA // 2 - 60))
            s = fonte_media.render("Pressione R para reiniciar", True, BRANCO)
            TELA.blit(s, (LARGURA // 2 - s.get_width() // 2, ALTURA // 2 + 20))

        elif estado == "vitoria":
            TELA.fill((20, 0, 40))
            t = fonte_grande.render("PARABÉNS!", True, AMARELO)
            TELA.blit(t, (LARGURA // 2 - t.get_width() // 2, ALTURA // 2 - 100))
            s1 = fonte_media.render("Você coletou todas as 4 chaves", True, BRANCO)
            TELA.blit(s1, (LARGURA // 2 - s1.get_width() // 2, ALTURA // 2 - 30))
            s2 = fonte_media.render("e fechou o Portal Mágico!", True, BRANCO)
            TELA.blit(s2, (LARGURA // 2 - s2.get_width() // 2, ALTURA // 2 + 10))
            s3 = fonte.render(f"Itens especiais coletados: {jogador.itens_especiais}", True, CIANO)
            TELA.blit(s3, (LARGURA // 2 - s3.get_width() // 2, ALTURA // 2 + 60))
            s4 = fonte_media.render("Pressione R para jogar novamente", True, VERDE)
            TELA.blit(s4, (LARGURA // 2 - s4.get_width() // 2, ALTURA // 2 + 120))

        pygame.display.flip()

if __name__ == "__main__":
    main()