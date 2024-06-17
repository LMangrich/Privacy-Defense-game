import pygame as pg
import constants as cons
import math
from projectile import Projectile
from turret_data import TURRET_DATA


class Turret(pg.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y, projectile_group):
        pg.sprite.Sprite.__init__(self)
        self.check_turret = 1
        self.range = TURRET_DATA[self.check_turret - 1].get("range")
        self.cooldown = TURRET_DATA[self.check_turret - 1].get("cooldown")
        self.selected = False
        self.target = None
        self.last_shot = pg.time.get_ticks()

        # position variables
        self.tile_x = tile_x
        self.tile_y = tile_y

        # calculate center coordinates
        self.x = (self.tile_x + 0.5) * cons.TILE_SIZE  # para ficar no centro do tile
        self.y = (self.tile_y + 0.35) * cons.TILE_SIZE
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        # create transparent circle showing range
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

        # reference to projectiles
        self.projectile_group = projectile_group

    def update(self, enemy_group):
        # if target picked, play firing animation
        if self.target:
            pass
        else:
            if pg.time.get_ticks() - self.last_shot > self.cooldown:
                self.pick_target(enemy_group)
    #TODO arrumar sobre fire projectile
    def fire_projectile(self):
        # create and add a projectile to the group
        if self.target:
            new_projectile = Projectile(self.rect.centerx, self.rect.centery, self.target.rect.centerx,
                                        self.target.rect.centery)
            self.projectile_group.add(new_projectile)
            self.target = None

    def pick_target(self, enemy_group):
        # find an enemy to target
        x_dist = 0
        y_dist = 0
        # check distance to each enemy to see if it is in range
        for enemy in enemy_group:
            x_dist = enemy.pos[0] - self.x
            y_dist = enemy.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < self.range:
                self.target = enemy
                print("Target selected")

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)
