import pygame as pg
import json
import time

from constants.constants import Constants
from classes.enemy_impl.enemy import Enemy
from classes.world_impl.world import World
from classes.turret_impl.turret import Turret
from classes.buttons_impl.button import Button
from classes.character_impl.character_dialogue import CharacterDialogue

from initialize.images.load_images import LoadImages
from initialize.game_variables.start_variables import GameVariables
from util import split_speech_into_lines

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

# def create_turret(mouse_pos, turret_type):
#     mouse_tile_x = mouse_pos[0] // cons.TILE_SIZE
#     mouse_tile_y = mouse_pos[1] // cons.TILE_SIZE
#     #calculate the sequential number of the tile
#     mouse_tile_num = (mouse_tile_y * cons.COLUMNS) + mouse_tile_x
#     #check if that tile is possible to put a turret
#
#     # Calcular a posição central do tile
#     tile_center_x = mouse_tile_x * cons.TILE_SIZE + cons.TILE_SIZE // 2
#     tile_center_y = mouse_tile_y * cons.TILE_SIZE + cons.TILE_SIZE // 2
#
#     # Calcular o número sequencial do tile
#     mouse_tile_num = (mouse_tile_y * cons.COLUMNS) + mouse_tile_x
#
#     #TODO VER AQUI PARA DELIMITAR POR COORDENADA X E Y, POR MOUSE TILE NUM NAO FUNCIONA
#     #if world.tile_map[mouse_tile_num] == 2: #o 1 aqui é o caminho TODO separar tal torre pequena para pontos especificos
#     #check that there isnt already a turret there
#     space_is_free = True
#     for turret in turret_group:
#         if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
#             space_is_free = False
#     #if it is a free space, then create turret
#     if space_is_free:
#         new_turret = Turret(turret_type, tile_center_x, tile_center_y, cons, images) #TODO por tudo isso só no de turret para funcionar, ver pq estava dando errado
#         turret_group.add(new_turret)


def create_turret(mouse_pos, turret_type):
    mouse_tile_x = mouse_pos[0] // cons.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // cons.TILE_SIZE

    # Verificar se o tile é válido para colocar uma torre
    if world.tile_map[mouse_tile_y][mouse_tile_x] == 2:  # Verifique se o tile é do tipo 2, que pode colocar torres
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False

        # Se o espaço estiver livre, crie a torre
        if space_is_free:
            print(f"Criando torre em ({mouse_tile_x}, {mouse_tile_y})")
            new_turret = Turret(turret_type, mouse_tile_x, mouse_tile_y, cons, images)
            turret_group.add(new_turret)
        else:
            print("Espaço já ocupado por outra torre.")
    else:
        print("Tile inválido para colocar torre.")


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

# phishing_enemy = Enemy(world.waypoints, images.phishing_enemy)
# keylogger_enemy = Enemy(world.waypoints, images.keylogger_enemy)
# spyware_enemy = Enemy(world.waypoints, images.spyware_enemy)
# malvertising_enemy = Enemy(world.waypoints, images.malvertising_enemy)
# databreach_enemy = Enemy(world.waypoints, images.databreach_enemy)
#
# enemy_group.add(phishing_enemy)  # instead of append, use add
# enemy_group.add(keylogger_enemy)  # instead of append, use add
# enemy_group.add(spyware_enemy)  # instead of append, use add
# enemy_group.add(malvertising_enemy)  # instead of append, use add
# enemy_group.add(databreach_enemy)  # instead of append, use add


#############################
# BUTTONS
#############################

information = Button(cons.SCREEN_WIDTH - 37, 8, images.information_button, True)  # TODO acrescentar funcionalidade
pause = Button(cons.SCREEN_WIDTH - 37, 45, images.pause_button, True)  # TODO acresentar funcionalidade

turret_buttons = {
    Button(259, 20, images.antivirus, True): images.cursor_get_antivirus, #first_turret
    Button(342, 17, images.firewall, True): images.cursor_get_firewall, #second turret
    Button(420, 17, images.strong_password, True): images.cursor_get_strong_password, #third turret
    Button(507, 16, images.filter_email, True): images.cursor_get_filter_email, #fourth turret
    Button(590, 17, images.usb_unknown, True): images.cursor_get_usb_unknown, #fifth turret
    Button(672, 17, images.unsafe_download, True): images.cursor_get_unsafe_download, #sixth turret
    Button(755, 17, images.adblock, True): images.cursor_get_adblock, #seventh turret
    Button(837, 17, images.change_password, True): images.cursor_get_change_password #eighth turret
}

# Adicionar variável para controlar o tempo
enemy_spawn_time = pg.time.get_ticks()
enemy_spawn_interval = 2000  # Intervalo de 2 segundos

def spawn_enemy():
    # Função para criar inimigos em intervalos de tempo
    current_time = pg.time.get_ticks()
    global enemy_spawn_time

    if current_time - enemy_spawn_time >= enemy_spawn_interval:
        enemy_type = [images.phishing_enemy, images.keylogger_enemy, images.spyware_enemy, images.malvertising_enemy,
                      images.databreach_enemy]
        enemy_image = enemy_type[len(enemy_group) % len(enemy_type)]
        new_enemy = Enemy(world.waypoints, enemy_image)
        enemy_group.add(new_enemy)
        enemy_spawn_time = current_time

#############################
# EXPLAINING GAME
#############################

dialogue = CharacterDialogue(images.character_one, images.footer_image, 90, cons.SCREEN_HEIGHT - 8, 480, cons.SCREEN_HEIGHT - 10, True, cons, images.antivirus, images.firewall, images.strong_password)

game_paused = True

#############################
# GAME START
#############################

with open("classes/character_impl/character_dialogue_data.json", encoding="utf-8") as file:
    speech_data = json.load(file)

speeches_queue = []

for speech in speech_data:
    print(speech["dialogue"])
    speeches_queue.append(speech["dialogue"])

indice_texto = 0
mouse_is_pressed = True
run = True
while run:
    clock.tick(cons.FPS)  # 60 fps

    screen.fill("grey100")  # atualiza a tela em td momento com o background

    # draw level
    world.draw(screen)
    information.draw(screen)
    pause.draw(screen)

    if len(speeches_queue) > 0:

        speech = speeches_queue[0]
        lines = split_speech_into_lines(speech)
        dialogue.draw(screen)
        font = pg.font.Font(None, 28)
        text = font.render(lines["first_line"], True, (255, 255, 255))
        text_rect = text.get_rect(center=(450, 550))
        screen.blit(text, text_rect)

        if pg.mouse.get_pressed()[0] == 1:
            #reset mouse pressed
            time.sleep(0.1)
            # Segundo pedaço do texto
            popet = speeches_queue.pop(0)

        #TODO arrumar a fala
        #TODO por uma seta
    else:
        #game_paused = 0
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

        for button, turret_type in turret_buttons.items():
            if button.draw(screen):
                game_variables.placing_turrets = True
                game_variables.current_turret_type = turret_type

        if game_variables.placing_turrets:
            # show cursor turret_impl
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:  # se clicar com o botão direito cancela
                game_variables.placing_turrets = False

        spawn_enemy()

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
                    create_turret(mouse_pos, game_variables.current_turret_type)
                else:
                    game_variables.selected_turret = select_turret(mouse_pos)
                # # Mostrar instruções se o jogo estiver em modo de explicação
                # if game_paused and dialogue.game_explication:
                #     dialogue.showInstructionsFirstPart()

    # update display
    pg.display.flip()

pg.quit()
