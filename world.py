import pygame as pg
import constants as cons


class World():
    def __init__(self, data, map_image):
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image

    def process_data(self):
        #look through data to extract relevant info
        for layer in self.level_data["layers"]:
            if layer["name"] == "Camada de Blocos 1":
                self.tile_map = layer["data"]
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    coordinate_x = obj["x"]
                    coordinate_y = obj["y"]
                    self.waypoints.append((coordinate_x, coordinate_y + cons.UPPER_PANEL))

    def draw(self, surface):
        surface.blit(self.image, (0, cons.UPPER_PANEL))
