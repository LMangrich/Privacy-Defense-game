class Constants:
    def __init__(self):
        self.ROWS = 13
        self.COLUMNS = 20
        self.TILE_SIZE = 48
        self.UPPER_PANEL = 89

        self.SCREEN_WIDTH = self.TILE_SIZE * self.COLUMNS
        self.SCREEN_HEIGHT = self.TILE_SIZE * self.ROWS
        self.FPS = 60