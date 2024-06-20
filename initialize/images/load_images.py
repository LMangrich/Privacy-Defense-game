import pygame as pg


class LoadImages(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        # Map images
        self.map_image = pg.image.load("assets/images/levels/firstLevel.png").convert_alpha()
        self.headerMap = pg.image.load("assets/images/buttons/headerMap.png").convert_alpha()
        self.information_button = pg.image.load("assets/images/buttons/informationButton.png").convert_alpha()
        self.pause_button = pg.image.load("assets/images/buttons/PauseButton.png").convert_alpha()

        # Turret images
        self.first_turret = pg.image.load("assets/images/buttons/firstTurret.png").convert_alpha()
        self.cursor_get_turret = pg.image.load("assets/images/turrets/Torre1AntiVirus.png").convert_alpha()

        # Character images
        self.character_one = pg.image.load("assets/images/characters/characterOne.png").convert_alpha()
        self.footer_image = pg.image.load("assets/images/characters/footerCharacter.png").convert_alpha()

        # Enemy images
        self.phishing_enemy = pg.image.load("assets/images/enemies/phishingEnemy.png").convert_alpha()

        # Buttons
        self.header_for_buying = pg.image.load("assets/images/buttons/headerMap.png").convert_alpha()
        self.buy_first_turret = pg.image.load("assets/images/buttons/firstTurret.png").convert_alpha()
        self.information_button = pg.image.load("assets/images/buttons/informationButton.png").convert_alpha()
        self.pause_button = pg.image.load("assets/images/buttons/pauseButton.png").convert_alpha()

