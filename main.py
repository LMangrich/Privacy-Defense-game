import pygame as pg
import json
import constants as cons

from enemy import Enemy #importa a classe Enemy do arquivo enemy
from world import World
from turret import Turret
from button import Button
from projectile import Projectile

############################# --> PYGAME LIB START
# Initialize pygame
pg.init()

#create clock
clock = pg.time.Clock()

screen = pg.display.set_mode((cons.SCREEN_WIDTH, cons.SCREEN_HEIGHT + cons.UPPER_PANEL))
pg.display.set_caption("Privacy Defense")

############################# --> MAP

#load images
map_image = pg.image.load("assets/images/levels/FirstLevel.png").convert_alpha()

#buttons
base_for_buying = pg.image.load("assets/images/buttons/ContornoMapaApenas.png").convert_alpha()
buy_first_turret = pg.image.load("assets/images/buttons/Torre1AntiVirus.png").convert_alpha()

#load json data for level
with open("assets/images/levels/FirstLevel.json") as file:
    world_data = json.load(file)

#create world
world = World(world_data, map_image)
world.process_data()

############################# --> TURRET

#game variables
placing_turrets = False
selected_turret = None

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
        new_turret = Turret(cursor_turret, mouse_tile_x, mouse_tile_y, projectile_group)
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

#individual turret image for mouse cursor
cursor_turret = pg.image.load("assets/images/turrets/Torre1AntiVirus.png").convert_alpha()

#create group
turret_group = pg.sprite.Group()
projectile_group = pg.sprite.Group()

############################# --> ENEMIES

#load images
enemy_image = pg.image.load("assets/images/enemies/Inimigo1Phising.png").convert_alpha()

#create groups for enemies
enemy_group = pg.sprite.Group() #similar to python list

enemy = Enemy(world.waypoints, enemy_image)
enemy_group.add(enemy) #instead of append, use add

############################# --> BUTTONS

base_buying = Button(0, 0, base_for_buying, True)
first_turret = Button(259, 20, buy_first_turret, True)

############################# --> GAME START
#game loop
run = True
while run:
    clock.tick(cons.FPS) #60 fps

    screen.fill("grey100") #atualiza a tela em td momento com o background

    #draw level
    world.draw(screen)

    #update groups
    enemy_group.update() #para lidar com vários inimigos
    turret_group.update(enemy_group)
    projectile_group.update()

    #hilight selected turret
    if selected_turret:
        selected_turret.selected = True

    #draw groups -> para aparecer na tela
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    projectile_group.draw(screen)

    #buttons
    base_buying.draw(screen)

    if first_turret.draw(screen):
        placing_turrets = True
    if placing_turrets:
        #show cursor turret
        cursor_rect = buy_first_turret.get_rect()
        cursor_pos = pg.mouse.get_pos()
        cursor_rect.center = cursor_pos
        if cursor_pos[1] >= cons.UPPER_PANEL:
            screen.blit(buy_first_turret, cursor_rect)
        if pg.mouse.get_pressed()[2] == 1: #se clicar com o botão direito cancela
            placing_turrets = False

    #event handler, lida com eventos em um for loop
    for event in pg.event.get():
        #quit program
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: #TODO mudar isso pq tem que ser caminhos especificos
            mouse_pos = pg.mouse.get_pos()
            #check if mouse is on the game area
            if mouse_pos[0] < cons.SCREEN_WIDTH and mouse_pos[1] >= cons.UPPER_PANEL:
                #clear selected turrets
                selected_turret = None
                clear_selection()
                if placing_turrets:
                    create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)
    #update display
    pg.display.flip()

pg.quit()
