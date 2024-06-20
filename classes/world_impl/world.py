class World:
    def __init__(self, data, map_image, header_map, constants):
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.header_map = header_map
        self.cons = constants

    def process_data(self):
        #look through data to extract relevant info
        for layer in self.level_data["layers"]:
            if layer["name"] == "Camada de Blocos 1":
                self.tile_map = layer["data"]
            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    coordinate_x = obj["x"]
                    coordinate_y = obj["y"]
                    self.waypoints.append((coordinate_x, coordinate_y + self.cons.UPPER_PANEL))

    def draw(self, surface):
        surface.blit(self.image, (0, self.cons.UPPER_PANEL))
        surface.blit(self.header_map, (0, 0))
