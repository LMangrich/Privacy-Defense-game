import pygame as pg
import constants as cons
import math

class Projectile(pg.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((8, 8))  # Ajuste o tamanho e a aparência conforme necessário
        self.image.fill((255, 0, 0))  # Cor vermelha para o projétil (pode ajustar a cor conforme desejar)
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)

        # Definir o vetor de direção para o alvo
        self.direction = pg.math.Vector2(target_x - start_x, target_y - start_y).normalize()

    def update(self):
        # Mover o projétil na direção do vetor normalizado
        self.rect.move_ip(self.direction.x * 5, self.direction.y * 5)  # Ajuste a velocidade conforme necessário

    def draw(self, surface):
        surface.blit(self.image, self.rect)
