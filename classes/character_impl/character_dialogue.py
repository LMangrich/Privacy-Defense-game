import pygame as pg


class CharacterDialogue(pg.sprite.Sprite):
    def __init__(self, image_character, image_footer, coordinate_x_character, coordinate_y_character,
                 coordinate_x_footer, coordinate_y_footer, game_explication, text):
        pg.sprite.Sprite.__init__(self)
        # position game_variables
        self.coordinate_x_character = coordinate_x_character
        self.coordinate_y_character = coordinate_y_character

        self.coordinate_y_footer = coordinate_y_footer
        self.coordinate_x_footer = coordinate_x_footer

        # check if game is up for explication
        self.game_explication = game_explication

        # images
        self.image_character = image_character
        self.rect_character = image_character.get_rect()
        self.rect_character.center = (self.coordinate_x_character, self.coordinate_y_character)

        self.image_footer = image_footer
        self.rect_footer = image_footer.get_rect()
        self.rect_footer.center = (self.coordinate_x_footer, self.coordinate_y_footer)

        # Text
        self.font = pg.font.Font(None, 36)
        self.text = text
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(
            bottomright=(self.coordinate_x_footer + 10, self.coordinate_y_footer + 10))

    def draw(self, surface):
        if self.game_explication:
            surface.blit(self.image_footer, self.rect_footer)
            surface.blit(self.image_character, self.rect_character)
            surface.blit(self.text_surface, self.text_rect)
