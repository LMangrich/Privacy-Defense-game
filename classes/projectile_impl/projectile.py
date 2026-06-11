import pygame as pg
import math

class Projectile(pg.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, target_enemy, damage=25, game_variables=None):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((8, 8))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)

        # Definir o vetor de direção para o alvo
        self.direction = pg.math.Vector2(target_x - start_x, target_y - start_y).normalize()
        self.start_pos = pg.math.Vector2(start_x, start_y)
        self.speed = 5
        self.target_enemy = target_enemy
        self.damage = damage
        self.has_hit = False
        self.game_variables = game_variables

    def update(self):
        # Mover o projétil na direção do vetor normalizado
        self.rect.move_ip(self.direction.x * self.speed, self.direction.y * self.speed)
        
        # Verificar colisão com o inimigo alvo
        if self.target_enemy and not self.has_hit:
            x_dist = self.target_enemy.pos[0] - self.rect.centerx
            y_dist = self.target_enemy.pos[1] - self.rect.centery
            distance = math.sqrt(x_dist ** 2 + y_dist ** 2)
            
            # Se o projétil atingiu o inimigo
            if distance < 20:  # Distância mínima para considerar como acerto
                self.target_enemy.take_damage(self.damage)
                
                # Dar recompensa se inimigo morreu
                if self.target_enemy.health <= 0 and self.game_variables:
                    self.game_variables.player_currency += 25
                
                self.has_hit = True
                self.kill()
        
        # Remover projétil se sair da tela
        if self.rect.y < 0 or self.rect.x < 0 or self.rect.x > 1920 or self.rect.y > 1080:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
