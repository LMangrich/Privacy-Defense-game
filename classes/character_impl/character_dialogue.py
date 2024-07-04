import pygame as pg
import json

class CharacterDialogue(pg.sprite.Sprite):
    def __init__(self, image_character, image_footer, coordinate_x_character, coordinate_y_character,
                 coordinate_x_footer, coordinate_y_footer, game_explication, text, turret_one, turret_two, turret_three):
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

        # turrets
        self.turret_one = turret_one
        self.turret_two = turret_two
        self.turret_three = turret_three

        self.rect_turret_one = turret_one.get_rect()
        self.rect_turret_one.topleft = (259, 20) # x  e y #TODO arrumar e por as corretas

        self.rect_turret_two = turret_two.get_rect()
        self.rect_turret_two.topleft  = (342, 17)  # x  e y

        self.rect_turret_three = turret_three.get_rect()
        self.rect_turret_three.topleft  = (420, 17)  # x  e y

        # Text
        self.font = pg.font.Font(None, 36)
        self.text_surface = None  # Inicializa como None

    def load_character_dialogues(self):
        with open("classes/character_impl/character_dialogue_data.json") as file:
            data = json.load(file)
        return data
    def showInstructionsFirstPart(self):
        self.dialogue_data = self.load_character_dialogues()

        for dialogue in self.dialogue_data:
            dialogue_id = dialogue['dialogue_id']
            dialogue_text = dialogue['dialogue']

            if dialogue_id == '6':
                break

            # Renderiza o texto do diálogo atual na tela
            self.text_surface = self.font.render(dialogue_text, True, (255, 255, 255))
            self.text_rect = self.text_surface.get_rect(bottomright=(self.coordinate_x_footer + 10, self.coordinate_y_footer + 10))

            wait_for_click = True
            while wait_for_click:
                for event in pg.event.get():
                    if event.type == pg.MOUSEBUTTONDOWN and event.button ==1:
                            wait_for_click = False

    def draw(self, surface):
        if self.game_explication:
            surface.blit(self.image_footer, self.rect_footer)
            surface.blit(self.image_character, self.rect_character)
            surface.blit(self.turret_one, self.rect_turret_one)
            surface.blit(self.turret_two, self.rect_turret_two)
            surface.blit(self.turret_three, self.rect_turret_three)
            #surface.blit(self.text_surface, self.text_rect)
