import pygame as pg
import json

from constants.constants import Constants
from classes.enemy_impl.enemy import Enemy
from classes.world_impl.world import World
from classes.turret_impl.turret import Turret
from classes.buttons_impl.button import Button
from classes.character_impl.character_dialogue import CharacterDialogue

from initialize.images.load_images import LoadImages
from initialize.game_variables.start_variables import GameVariables


#############################
# PYGAME LIB START
#############################

# Initialize pygame
pg.init()

# create clock
clock = pg.time.Clock()

#############################
# Constants
#############################

cons = Constants()

#############################
# Game_variables
#############################

game_variables = GameVariables()

# create screen
screen = pg.display.set_mode((cons.SCREEN_WIDTH, cons.SCREEN_HEIGHT + cons.UPPER_PANEL))
pg.display.set_caption("Privacy Defense")

#############################
# LOAD IMAGES
#############################

images = LoadImages()

#############################
# MAP
#############################

# load json data for level
with open("assets/images/levels/firstLevel.json") as file: #TODO por as coordenadas de onde por as torres aqui
    world_data = json.load(file)

# create world_impl
world = World(world_data, images.map_image, images.headerMap, cons)
world.process_data()

#############################
# TURRET
#############################

turret_group = pg.sprite.Group()

def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // cons.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // cons.TILE_SIZE
    #calculate the sequential number of the tile
    mouse_tile_num = (mouse_tile_y * cons.COLUMNS) + mouse_tile_x
    #check if that tile is possible to put a turret
    #TODO VER AQUI PARA DELIMITAR POR COORDENADA X E Y, POR MOUSE TILE NUM NAO FUNCIONA
    #if world.tile_map[mouse_tile_num] == 2: #o 1 aqui é o caminho TODO separar tal torre pequena para pontos especificos
    #check that there isnt already a turret there
    space_is_free = True
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            space_is_free = False
    #if it is a free space, then create turret
    if space_is_free:
        new_turret = Turret(images.cursor_get_turret, mouse_tile_x, mouse_tile_y, cons, images) #TODO por tudo isso só no de turret para funcionar, ver pq estava dando errado
        turret_group.add(new_turret)

def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // cons.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // cons.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret

def clear_selection():
    for turret in turret_group:
        turret.selected = False

#############################
# ENEMIES
#############################

# create groups for enemies
enemy_group = pg.sprite.Group()  # similar to python list

phishing_enemy = Enemy(world.waypoints, images.phishing_enemy)
enemy_group.add(phishing_enemy)  # instead of append, use add

#############################
# BUTTONS
#############################

first_turret = Button(259, 20, images.first_turret, True)
information = Button(cons.SCREEN_WIDTH - 37, 8, images.information_button, True)  # TODO acrescentar funcionalidade
pause = Button(cons.SCREEN_WIDTH - 37, 45, images.pause_button, True)  # TODO acresentar funcionalidade

#############################
# EXPLAINING GAME
#############################

dialogue = CharacterDialogue(images.character_one, images.footer_image, 90, cons.SCREEN_HEIGHT - 8, 480, cons.SCREEN_HEIGHT - 10, True, cons)

game_paused = True

def show_instructions(): #TODO ver sobre o texto
    font = pg.font.Font(None, 36)
    text = font.render("Clique para começar", True, (255, 255, 255))
    text_rect = text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

def load_character_dialogues():
    with open("classes/character_impl/character_dialogue_data.json") as file:
        data = json.load(file)
    return data

def showInstructionsFirstPart():
    dialogue_data = load_character_dialogues()

    for dialogue in dialogue_data:
        dialogue_id = dialogue['dialogue_id']
        dialogue_text = dialogue['dialogue']

        if dialogue_id == '6':
            break

        # Renderiza o texto do diálogo atual na tela
        font = pg.font.Font(None, 36)
        text_surface = font.render(dialogue_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            bottomright=(300, 300))

        wait_for_click = True
        while wait_for_click:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    wait_for_click = False

#############################
# GAME START
#############################

run = True
while run:
    clock.tick(cons.FPS)  # 60 fps

    screen.fill("grey100")  # atualiza a tela em td momento com o background

    # draw level
    world.draw(screen)
    information.draw(screen)
    pause.draw(screen)

    if game_paused:
        # draw first character_impl

        dialogue.draw(screen)

        show_instructions()
        #showInstructionsFirstPart()

        # show information when click
        if pg.mouse.get_pressed()[0] == 1:
            game_paused = False  # return game
    else:

        # update groups
        enemy_group.update()  # para lidar com vários inimigos
        turret_group.update(enemy_group)

        # hilight selected turret_impl
        if game_variables.selected_turret:
            game_variables.selected_turret.selected = True

        # draw groups -> para aparecer na tela
        enemy_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)

        # buttons

        if first_turret.draw(screen):
            game_variables.placing_turrets = True
        if game_variables.placing_turrets:
            # show cursor turret_impl
            cursor_rect = images.buy_first_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(images.buy_first_turret, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:  # se clicar com o botão direito cancela
                game_variables.placing_turrets = False

    # event handler, lida com eventos em um for loop
    for event in pg.event.get():
        # quit program
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # TODO mudar isso pq tem que ser caminhos especificos
            mouse_pos = pg.mouse.get_pos()
            # check if mouse is on the game area
            if mouse_pos[0] < cons.SCREEN_WIDTH and mouse_pos[1] >= cons.UPPER_PANEL:
                # clear selected turrets
                game_variables.selected_turret = None
                clear_selection()
                if game_variables.placing_turrets:
                    create_turret(mouse_pos)
                else:
                    game_variables.selected_turret = select_turret(mouse_pos)
                # Mostrar instruções se o jogo estiver em modo de explicação
                if game_paused and dialogue.game_explication:
                    dialogue.showInstructionsFirstPart()

    # update display
    pg.display.flip()

pg.quit()
