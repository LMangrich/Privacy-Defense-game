import pygame as pg
from pygame.math import Vector2
import math

class Enemy(pg.sprite.Sprite): #o sprite class tem um draw method mesmo nao tendo explicito por conta do pygame
    def __init__(self, waypoints, image): #funciona como construtor da classe
        pg.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0]) #com isso consegue pegar as posiçoes, mas o pos é o inicial
        self.target_waypoint = 1 #o vetor começa do 0, entao pega o 1 como sendo a prox posicao
        self.speed = 2
        self.angle = 0
        self.original_image = image
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect() #retorna um retângulo (Rect) que define a posição e as dimensões da imagem
        self.rect.center = self.pos

    def update(self):
        self.move()
        self.rotate()

    def move(self):
        #define a target waypoint
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos #distancia entre os 2 waypoints
        else:
            #enemy has reached the end of the path
            self.kill()

        #calculate distance to target
        dist = self.movement.length()
        #check if remaining distance is greater than the enemy speed
        if dist >= self.speed:
            self.pos += self.movement.normalize() * self.speed
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

    def rotate(self):
        #calculate distance to next waypoint
        dist = self.target - self.pos
        #use distance to calculate angle
        self.angle = math.degrees(math.atan2(dist[1], dist[0])) #TODO ver sobre isso ainda
        #rotate image and update reactangle
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
