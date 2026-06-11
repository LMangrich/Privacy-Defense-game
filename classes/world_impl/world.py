import pygame as pg


class World:
    def __init__(self, data, map_image, header_map, constants):
        self.tile_map = []
        self.waypoints = []
        self.tower_zones = []
        self.level_data = data
        self.image = map_image
        self.header_map = header_map
        self.cons = constants

    def process_data(self):
        #look through data to extract relevant info
        for layer in self.level_data["layers"]:
            if layer["name"] == "Camada de Blocos 1":
                tile_map_1d = layer["data"]
                self.tile_map = [tile_map_1d[i:i + self.cons.COLUMNS] for i in range(0, len(tile_map_1d), self.cons.COLUMNS)]
            elif layer["name"] == "Zona de torres":
                for obj in layer.get("objects", []):
                    x = obj.get("x", 0)
                    y = obj.get("y", 0)
                    obj_width = obj.get("width", 0)
                    obj_height = obj.get("height", 0)

                    # Keep coordinates strictly relative to the map (0,0 is top-left of map)
                    if obj_width and obj_height:
                        zone_rect = pg.Rect(int(x), int(y), int(obj_width), int(obj_height))
                    else:
                        zone_rect = pg.Rect(
                            int(x - self.cons.TILE_SIZE / 2),
                            int(y - self.cons.TILE_SIZE / 2),
                            self.cons.TILE_SIZE,
                            self.cons.TILE_SIZE,
                        )

                    self.tower_zones.append(zone_rect)
            elif layer["name"] == "waypoints":
                ordered_objects = sorted(layer.get("objects", []), key=lambda item: item.get("id", 0))
                for obj in ordered_objects:
                    coordinate_x = obj["x"]
                    coordinate_y = obj["y"]
                    self.waypoints.append((coordinate_x, coordinate_y + self.cons.UPPER_PANEL))

        if not self.tower_zones and self.tile_map:
            for row_index, row in enumerate(self.tile_map):
                for col_index, tile in enumerate(row):
                    if tile == 2:
                        self.tower_zones.append(
                            pg.Rect(
                                col_index * self.cons.TILE_SIZE,
                                row_index * self.cons.TILE_SIZE,
                                self.cons.TILE_SIZE,
                                self.cons.TILE_SIZE,
                            )
                        )

    def draw(self, surface):
        surface.blit(self.image, (0, self.cons.UPPER_PANEL))
        surface.blit(self.header_map, (0, 0))
