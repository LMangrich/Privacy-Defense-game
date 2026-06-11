import pygame as pg
import json

from constants.constants import Constants
from classes.world_impl.world import World
from classes.buttons_impl.button import Button
from classes.character_impl.character_dialogue import CharacterDialogue

from initialize.images.load_images import LoadImages
from initialize.game_variables.start_variables import GameVariables
from game.dialogue_loader import load_all_dialogues, load_level_dialogue
from game.gameplay import (
    create_turret,
    select_turret,
    clear_selection,
    spawn_enemy_wave,
    reset_level,
)
from game.ui import draw_ui
from game.ui import draw_dialogue_footer

#############################
# PYGAME LIB START
#############################

pg.init()
clock = pg.time.Clock()
cons = Constants()
game_variables = GameVariables()

screen = pg.display.set_mode((cons.SCREEN_WIDTH, cons.SCREEN_HEIGHT))
pg.display.set_caption("Privacy Defense")

images = LoadImages()

#############################
# CHARACTER DIALOGUE
#############################

dialogue = CharacterDialogue(
    images.character_one,
    images.footer_image,
    80,
    cons.UPPER_PANEL + cons.MAP_HEIGHT + (cons.LOWER_PANEL // 2),
    480,
    cons.UPPER_PANEL + cons.MAP_HEIGHT + (cons.LOWER_PANEL // 2),
    True,
    cons,
    images.antivirus,
    images.firewall,
    images.strong_password,
)

#############################
# MAP & WORLD
#############################

with open("assets/images/levels/firstLevel.json") as file:
    world_data = json.load(file)

world = World(world_data, images.map_image, images.headerMap, cons)
world.process_data()

#############################
# GAME STATE
#############################

turret_group = pg.sprite.Group()
projectile_group = pg.sprite.Group()
enemy_group = pg.sprite.Group()

current_level = 1
game_state = "dialogue_intro"
dialogue_index = 0
level_start_time = None
enemy_wave_spawned = 0
game_over_message = ""
showing_game_over = False
game_over_time = None
victory_message = ""

#############################
# LOAD DIALOGUE DATA
#############################

all_dialogue_data = load_all_dialogues("classes/character_impl/character_dialogue_data.json")
current_dialogue_data = load_level_dialogue(all_dialogue_data, current_level)
intro_sequence = current_dialogue_data.get("intro_dialogues", []) + current_dialogue_data.get("tower_explanation", [])

#############################
# GAME FUNCTIONS
#############################

def apply_reset(level):
    global game_state, dialogue_index, enemy_wave_spawned, showing_game_over
    global game_over_message, current_dialogue_data, intro_sequence, level_start_time, victory_message

    reset_data = reset_level(
        level,
        game_variables,
        turret_group,
        projectile_group,
        enemy_group,
        load_level_dialogue,
        all_dialogue_data,
    )

    game_state = reset_data["game_state"]
    dialogue_index = reset_data["dialogue_index"]
    enemy_wave_spawned = reset_data["enemy_wave_spawned"]
    showing_game_over = reset_data["showing_game_over"]
    game_over_message = reset_data["game_over_message"]
    current_dialogue_data = reset_data["current_dialogue_data"]
    level_start_time = reset_data["level_start_time"]
    intro_sequence = current_dialogue_data.get("intro_dialogues", []) + current_dialogue_data.get("tower_explanation", [])
    victory_message = ""


def draw_enemy_path_hints():
    overlay = pg.Surface((cons.SCREEN_WIDTH, cons.SCREEN_HEIGHT), pg.SRCALPHA)

    for waypoint in world.waypoints:
        center_x = int(waypoint[0])
        center_y = int(waypoint[1])
        pg.draw.circle(overlay, (0, 200, 255, 85), (center_x, center_y), 14, 2)

    if len(world.waypoints) > 1:
        pg.draw.lines(overlay, (0, 200, 255, 60), False, [(int(x), int(y)) for (x, y) in world.waypoints], 2)

    screen.blit(overlay, (0, 0))


def draw_tower_placement_hints():
    overlay = pg.Surface((cons.SCREEN_WIDTH, cons.SCREEN_HEIGHT), pg.SRCALPHA)

    for zone in world.tower_zones:
        center_x = int(zone.centerx)
        center_y = int(zone.centery + cons.UPPER_PANEL)
        pg.draw.circle(overlay, (0, 255, 120, 80), (center_x, center_y), 10, 2)

    screen.blit(overlay, (0, 0))


def draw_tower_button_highlight(level):
    button_list = list(turret_buttons.keys())
    tower_index = min(max(level - 1, 0), 2)
    if tower_index < len(button_list):
        target_button = button_list[tower_index]
        center = target_button.rect.center
        radius = max(target_button.rect.width, target_button.rect.height) // 2 + 10
        pg.draw.circle(screen, (255, 215, 0), center, radius, 3)


def draw_tower_costs():
    """Desenha o custo das torres sob seus ícones"""
    from classes.turret_impl.turret_data import TURRET_DATA
    
    font_cost = pg.font.Font(None, 20)
    
    # Mapear índice global das torres para índice no TURRET_DATA
    tower_index_map = {
        0: 0,  # Antivirus
        1: 1,  # Firewall
        2: 2,  # Strong Password
        3: 3,  # Filter Email
        4: 4,  # USB Unknown
        5: 5,  # Unsafe Download
        6: 6,  # Adblock
        7: 7,  # Change Password
    }
    
    for visual_index, (button, turret_type) in enumerate(get_unlocked_turret_buttons(current_level)):
        tower_data_index = tower_index_map.get(visual_index, 0)
        cost = TURRET_DATA[tower_data_index]["cost"]
        
        cost_text = font_cost.render(str(cost), True, (255, 215, 0))
        cost_rect = cost_text.get_rect(center=(button.rect.centerx + 25, button.rect.bottom + 10))
        screen.blit(cost_text, cost_rect)

#############################
# BUTTONS
#############################

information = Button(cons.SCREEN_WIDTH - 37, 8, images.information_button, True)
pause = Button(cons.SCREEN_WIDTH - 37, 45, images.pause_button, True)

turret_buttons = {
    Button(259, 20, images.antivirus, True): images.cursor_get_antivirus,
    Button(342, 17, images.firewall, True): images.cursor_get_firewall,
    Button(420, 17, images.strong_password, True): images.cursor_get_strong_password,
    Button(507, 16, images.filter_email, True): images.cursor_get_filter_email,
    Button(590, 17, images.usb_unknown, True): images.cursor_get_usb_unknown,
    Button(672, 17, images.unsafe_download, True): images.cursor_get_unsafe_download,
    Button(755, 17, images.adblock, True): images.cursor_get_adblock,
    Button(837, 17, images.change_password, True): images.cursor_get_change_password
}


def get_unlocked_turret_buttons(level):
    ordered_items = list(turret_buttons.items())
    unlocked_count_by_level = {
        1: 1,
        2: 2,
        3: 3,
    }
    unlocked_count = unlocked_count_by_level.get(level, 3)
    return ordered_items[:unlocked_count]

#############################
# MAIN GAME LOOP
#############################

run = True
while run:
    clock.tick(cons.FPS)
    screen.fill("grey100")

    dialogue_center = (
        cons.SCREEN_WIDTH // 2,
        cons.UPPER_PANEL + cons.MAP_HEIGHT + (cons.LOWER_PANEL // 2),
    )
    footer_y = cons.UPPER_PANEL + cons.MAP_HEIGHT
    footer_text = ""
    
    world.draw(screen)
    information.draw(screen)
    pause.draw(screen)
    
    if game_state == "dialogue_intro":
        # Desenha torres colocadas durante diálogo
        enemy_group.draw(screen)
        projectile_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)
        
        # Permite colocação de torres durante diálogo
        for button, turret_type in get_unlocked_turret_buttons(current_level):
            if button.draw(screen):
                game_variables.placing_turrets = True
                game_variables.current_turret_type = turret_type
        
        draw_tower_costs()

        if game_variables.placing_turrets:
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:
                game_variables.placing_turrets = False
        
        if dialogue_index < len(current_dialogue_data.get("intro_dialogues", [])):
            footer_text = current_dialogue_data["intro_dialogues"][dialogue_index]
            if dialogue_index == 1:
                draw_enemy_path_hints()
            if dialogue_index == 2:
                draw_tower_placement_hints()
        elif dialogue_index < len(intro_sequence):
            tower_text_index = dialogue_index - len(current_dialogue_data.get("intro_dialogues", []))
            footer_text = current_dialogue_data["tower_explanation"][tower_text_index]
            draw_tower_button_highlight(current_level)
        else:
            game_state = "waiting_for_start"
    
    elif game_state == "waiting_for_start":
        enemy_intro = current_dialogue_data.get("enemy_intro", "")
        if enemy_intro:
            footer_text = enemy_intro

        font_start = pg.font.Font(None, 36)
        start_text = font_start.render("Pressione ENTER para começar!", True, (255, 255, 0))
        text_rect = start_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + cons.MAP_HEIGHT // 2 + 40))
        screen.blit(start_text, text_rect)

        draw_enemy_path_hints()
        
        # Desenha torres já colocadas
        for turret in turret_group:
            turret.draw(screen)

        for button, turret_type in get_unlocked_turret_buttons(current_level):
            if button.draw(screen):
                game_variables.placing_turrets = True
                game_variables.current_turret_type = turret_type

        draw_tower_costs()

        if game_variables.placing_turrets:
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:
                game_variables.placing_turrets = False

        draw_ui(screen, cons, game_variables)
    
    elif game_state == "playing":
        enemy_wave_spawned = spawn_enemy_wave(
            current_level,
            level_start_time,
            enemy_wave_spawned,
            images,
            world,
            enemy_group,
            game_variables,
        )
        
        enemy_group.update()
        turret_group.update(enemy_group, projectile_group)
        projectile_group.update()
        
        if game_variables.computer_health <= 0:
            game_state = "game_over"
            showing_game_over = True
            game_over_time = pg.time.get_ticks()
            game_over_message = current_dialogue_data["defeat_dialogue"][0]
        
        if len(enemy_group) == 0 and enemy_wave_spawned > 0 and game_variables.computer_health > 0:
            victory_message = current_dialogue_data.get("victory_dialogue", ["Nível concluído!"])[0]
            game_state = "victory_dialogue"
        
        if game_variables.selected_turret:
            game_variables.selected_turret.selected = True
        
        enemy_group.draw(screen)
        projectile_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)
        
        for button, turret_type in get_unlocked_turret_buttons(current_level):
            if button.draw(screen):
                game_variables.placing_turrets = True
                game_variables.current_turret_type = turret_type
        
        draw_tower_costs()
        
        if game_variables.placing_turrets:
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:
                game_variables.placing_turrets = False
        
        draw_ui(screen, cons, game_variables)
        footer_text = current_dialogue_data.get("enemy_intro", "")
    
    elif game_state == "victory_dialogue":
        footer_text = victory_message

        font_continue = pg.font.Font(None, 32)
        continue_text = font_continue.render("Clique para continuar", True, (255, 255, 0))
        continue_rect = continue_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + cons.MAP_HEIGHT // 2 + 70))
        screen.blit(continue_text, continue_rect)

        if current_level == 3:
            font_end = pg.font.Font(None, 42)
            end_text = font_end.render("Parabéns! Você completou o jogo!", True, (255, 215, 0))
            end_rect = end_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + cons.MAP_HEIGHT // 2 - 70))
            screen.blit(end_text, end_rect)
    
    elif game_state == "game_over":
        if showing_game_over:
            footer_text = game_over_message

            font_restart = pg.font.Font(None, 32)
            restart_text = font_restart.render("Pressione R para tentar novamente", True, (255, 255, 0))
            restart_rect = restart_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + cons.MAP_HEIGHT // 2 + 70))
            screen.blit(restart_text, restart_rect)

    draw_dialogue_footer(
        screen,
        cons,
        footer_y,
        footer_text,
        images.character_one,
        images.footer_image,
    )
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        
        if event.type == pg.KEYDOWN and event.key == pg.K_RETURN and game_state == "waiting_for_start":
            game_state = "playing"
            level_start_time = pg.time.get_ticks()

        if event.type == pg.KEYDOWN and event.key == pg.K_r and game_state == "game_over":
            apply_reset(current_level)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and game_state == "dialogue_intro":
            mouse_pos = pg.mouse.get_pos()
            # Se clicou no mapa, pode colocar torres
            if cons.UPPER_PANEL <= mouse_pos[1] < cons.UPPER_PANEL + cons.MAP_HEIGHT:
                if game_variables.placing_turrets:
                    create_turret(
                        mouse_pos,
                        game_variables.current_turret_type,
                        cons,
                        world,
                        turret_group,
                        game_variables,
                        images,
                    )
            else:
                # Se clicou fora do mapa, avança diálogo
                if dialogue_index < len(intro_sequence):
                    dialogue_index += 1

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and game_state == "victory_dialogue":
            if current_level < 3:
                current_level += 1
                apply_reset(current_level)
            else:
                run = False
        
        if game_state in {"playing", "waiting_for_start"} and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            if cons.UPPER_PANEL <= mouse_pos[1] < cons.UPPER_PANEL + cons.MAP_HEIGHT:
                game_variables.selected_turret = None
                clear_selection(turret_group)
                if game_variables.placing_turrets:
                    create_turret(
                        mouse_pos,
                        game_variables.current_turret_type,
                        cons,
                        world,
                        turret_group,
                        game_variables,
                        images,
                    )
                else:
                    game_variables.selected_turret = select_turret(mouse_pos, cons, turret_group)
    
    pg.display.flip()

pg.quit()
