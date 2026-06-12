import pygame as pg
import math

from constants.constants import DEBUG
from .turret_data import TURRET_DATA
from ..projectile_impl.projectile import Projectile

class Turret(pg.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y, constants, images, game_variables=None, turret_index=0):
        pg.sprite.Sprite.__init__(self)
        # Mantido por compatibilidade; turret_index define qual torre do TURRET_DATA usar
        self.turret_index = turret_index
        self.check_turret = turret_index + 1
        turret_stats = TURRET_DATA[turret_index]
        self.range = turret_stats.get("range")
        self.cooldown = turret_stats.get("cooldown")
        self.damage = turret_stats.get("damage", 25)
        self.selected = False
        self.target = None
        self.last_shot = pg.time.get_ticks()
        self.cons = constants
        self.images = images
        self.game_variables = game_variables

        # position game_variables
        self.tile_x = tile_x
        self.tile_y = tile_y

        # calculate center coordinates
        self.x = (self.tile_x + 0.5) * self.cons.TILE_SIZE  # para ficar no centro do tile
        self.y = ((self.tile_y + 0.5) * self.cons.TILE_SIZE) + self.cons.UPPER_PANEL # ajustar para ficar no centro do tile
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

    def update(self, enemy_group, projectile_group):
        # if target picked, check if still in range and fire
        if self.target:
            # Check if target is still in range
            x_dist = self.target.pos[0] - self.x
            y_dist = self.target.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            
            # If target out of range, clear it
            if dist > self.range:
                self.target = None
            # If target in range and cooldown ready, fire
            elif pg.time.get_ticks() - self.last_shot > self.cooldown:
                self.fire(projectile_group)
        else:
            # Pick a new target if cooldown is ready
            if pg.time.get_ticks() - self.last_shot > self.cooldown:
                self.pick_target(enemy_group)

    # TODO arrumar sobre fire projectile_impl

    def fire(self, projectile_group):
        """Create and fire a projectile at the target"""
        if self.target:
            projectile = Projectile(self.x, self.y, self.target.pos[0], self.target.pos[1], self.target, self.damage, self.game_variables)
            projectile_group.add(projectile)
            self.last_shot = pg.time.get_ticks()
            self.target = None
            if DEBUG:
                print(f"Turret fired! Damage: {self.damage}")

    def pick_target(self, enemy_group):
        # find an enemy_impl to target
        x_dist = 0
        y_dist = 0
        # check distance to each enemy_impl to see if it is in range
        for enemy in enemy_group:
            x_dist = enemy.pos[0] - self.x
            y_dist = enemy.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < self.range:
                self.target = enemy
                if DEBUG:
                    print("Target selected")

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)
