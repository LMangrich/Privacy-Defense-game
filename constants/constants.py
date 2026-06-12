# Ative para imprimir mensagens de debug no console
DEBUG = False


class Constants:
    def __init__(self):
        self.ROWS = 13
        self.COLUMNS = 20
        self.TILE_SIZE = 48
        self.UPPER_PANEL = 89
        self.LOWER_PANEL = 180

        self.MAP_WIDTH = self.TILE_SIZE * self.COLUMNS
        self.MAP_HEIGHT = self.TILE_SIZE * self.ROWS

        self.SCREEN_WIDTH = self.MAP_WIDTH
        self.SCREEN_HEIGHT = self.UPPER_PANEL + self.MAP_HEIGHT + self.LOWER_PANEL
        self.FPS = 60