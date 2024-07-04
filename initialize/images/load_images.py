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
        self.antivirus = pg.image.load("assets/images/buttons/antivirus.png").convert_alpha()
        self.cursor_get_antivirus = pg.image.load("assets/images/turrets/Torre1AntiVirus.png").convert_alpha()

        self.firewall = pg.image.load("assets/images/buttons/firewall.png").convert_alpha()
        self.cursor_get_firewall = pg.image.load("assets/images/turrets/firewall.png").convert_alpha()

        self.strong_password = pg.image.load("assets/images/buttons/senhaforte.png").convert_alpha()
        self.cursor_get_strong_password = pg.image.load("assets/images/turrets/senhaforte.png").convert_alpha()

        self.filter_email = pg.image.load("assets/images/buttons/filtroemail.png").convert_alpha()
        self.cursor_get_filter_email = pg.image.load("assets/images/turrets/filtroemail.png").convert_alpha()

        self.usb_unknown = pg.image.load("assets/images/buttons/usbdesconhecido.png").convert_alpha()
        self.cursor_get_usb_unknown = pg.image.load("assets/images/turrets/usbdesconhecido.png").convert_alpha()

        self.unsafe_download = pg.image.load("assets/images/buttons/downloadsuspeito.png").convert_alpha()
        self.cursor_get_unsafe_download = pg.image.load("assets/images/turrets/downloadsuspeito.png").convert_alpha()

        self.adblock = pg.image.load("assets/images/buttons/adblock.png").convert_alpha()
        self.cursor_get_adblock = pg.image.load("assets/images/turrets/adblock.png").convert_alpha()

        self.change_password = pg.image.load("assets/images/buttons/trocasenhas.png").convert_alpha()
        self.cursor_get_change_password = pg.image.load("assets/images/turrets/trocasenhas.png").convert_alpha()

        # Character images
        self.character_one = pg.image.load("assets/images/characters/characterOne.png").convert_alpha()
        self.footer_image = pg.image.load("assets/images/characters/footerCharacter.png").convert_alpha()

        # Enemy images
        self.phishing_enemy = pg.image.load("assets/images/enemies/phishingEnemy.png").convert_alpha()
        self.phishing_enemy_bigger_size = pg.image.load("assets/images/enemies/phishingEnemy.png").convert_alpha()

        self.keylogger_enemy = pg.image.load("assets/images/enemies/keylogger.png").convert_alpha()

        self.spyware_enemy = pg.image.load("assets/images/enemies/spyware.png").convert_alpha()

        self.malvertising_enemy = pg.image.load("assets/images/enemies/malvertising.png").convert_alpha()

        self.databreach_enemy = pg.image.load("assets/images/enemies/databreach.png").convert_alpha()


        # Buttons
        self.header_for_buying = pg.image.load("assets/images/buttons/headerMap.png").convert_alpha()
        self.buy_first_turret = pg.image.load("assets/images/buttons/antivirus.png").convert_alpha()
        self.information_button = pg.image.load("assets/images/buttons/informationButton.png").convert_alpha()
        self.pause_button = pg.image.load("assets/images/buttons/pauseButton.png").convert_alpha()

