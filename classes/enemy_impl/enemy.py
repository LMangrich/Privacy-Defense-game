import pygame as pg
from pygame.math import Vector2
import math


class Enemy(pg.sprite.Sprite):  # o sprite class tem um draw method mesmo nao tendo explicito por conta do pygame
    def __init__(self, waypoints, image, health=100, on_reach_end=None, speed=2):  # funciona como construtor da classe
        pg.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0])  # com isso consegue pegar as posiçoes, mas o pos é o inicial
        self.target_waypoint = 1  # o vetor começa do 0, entao pega o 1 como sendo a prox posicao
        self.speed = speed
        self.angle = 0
        self.original_image = image
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()  # retorna um retângulo (Rect) que define a posição e as dimensões da imagem
        self.rect.center = self.pos
        
        # Health system
        self.health = health
        self.max_health = health
        
        # Callback when reaching end
        self.on_reach_end = on_reach_end

    def update(self):
        self.move()
        self.rotate()

    def move(self):
        # define a target waypoint
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos  # distancia entre os 2 waypoints
        else:
            # enemy_impl has reached the end of the path
            if self.on_reach_end:
                self.on_reach_end()
            self.kill()
            return

        # calculate distance to target
        dist = self.movement.length()
        # check if remaining distance is greater than the enemy_impl speed
        if dist >= self.speed:
            self.pos += self.movement.normalize() * self.speed
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        # calculate distance to next waypoint
        dist = self.target - self.pos
        # use distance to calculate angle
        self.angle = math.degrees(math.atan2(dist[1], dist[0]))  # TODO ver sobre isso ainda
        # rotate image and update reactangle
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def take_damage(self, damage):
        """Apply damage to enemy and remove if health reaches 0"""
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, surface):
        """Desenha uma pequena barra de vida acima do inimigo quando ele esta ferido."""
        if self.health >= self.max_health:
            return

        bar_width = 30
        bar_height = 5
        ratio = max(self.health, 0) / self.max_health
        bar_x = int(self.pos[0] - bar_width / 2)
        bar_y = int(self.rect.top - 8)

        pg.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        bar_color = (0, 220, 0) if ratio > 0.5 else (255, 165, 0) if ratio > 0.25 else (220, 0, 0)
        pg.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_width * ratio), bar_height))
