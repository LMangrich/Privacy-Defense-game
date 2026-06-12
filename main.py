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
from game.ui import draw_turret_tooltip
from game import level_config
from classes.turret_impl.turret_data import TURRET_DATA

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

world = None


def load_level_world(level):
    """Carrega o mapa (imagem + JSON) da fase e recria o mundo."""
    global world
    images.map_image = pg.image.load(level_config.map_image_path(level)).convert_alpha()
    with open(level_config.map_json_path(level), encoding="utf-8") as file:
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
paused = False
pause_started_at = None
feedback_message = ""
feedback_message_time = 0

#############################
# LOAD DIALOGUE DATA
#############################

all_dialogue_data = load_all_dialogues("classes/character_impl/character_dialogue_data.json")
current_dialogue_data = load_level_dialogue(all_dialogue_data, current_level)
intro_sequence = current_dialogue_data.get("intro_dialogues", []) + current_dialogue_data.get("tower_explanation", [])

# Carrega o mapa da primeira fase
load_level_world(current_level)

#############################
# GAME FUNCTIONS
#############################

def apply_reset(level):
    global game_state, dialogue_index, enemy_wave_spawned, showing_game_over
    global game_over_message, current_dialogue_data, intro_sequence, level_start_time, victory_message

    # Recarrega o mapa correspondente à fase (muda ao avançar de nível)
    load_level_world(level)

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
    tower_index = min(max(level - 1, 0), len(button_list) - 1)
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

        affordable = game_variables.player_currency >= cost
        cost_color = (255, 215, 0) if affordable else (130, 130, 130)
        cost_text = font_cost.render(str(cost), True, cost_color)
        cost_rect = cost_text.get_rect(center=(button.rect.centerx + 25, button.rect.bottom + 10))
        screen.blit(cost_text, cost_rect)


def get_cursor_turret_index(turret_type):
    """Mapeia a imagem do cursor de torre para o indice no TURRET_DATA."""
    cursor_to_index = {
        images.cursor_get_antivirus: 0,
        images.cursor_get_firewall: 1,
        images.cursor_get_strong_password: 2,
        images.cursor_get_filter_email: 3,
        images.cursor_get_usb_unknown: 4,
        images.cursor_get_unsafe_download: 5,
        images.cursor_get_adblock: 6,
        images.cursor_get_change_password: 7,
    }
    return cursor_to_index.get(turret_type, 0)


def draw_placement_overlay():
    """Destaca as zonas validas e mostra o alcance da torre durante a colocacao."""
    if not game_variables.placing_turrets:
        return
    from classes.turret_impl.turret_data import TURRET_DATA

    draw_tower_placement_hints()

    cursor_pos = pg.mouse.get_pos()
    if cursor_pos[1] >= cons.UPPER_PANEL:
        turret_index = get_cursor_turret_index(game_variables.current_turret_type)
        turret_range = TURRET_DATA[turret_index]["range"]
        range_overlay = pg.Surface((turret_range * 2, turret_range * 2), pg.SRCALPHA)
        pg.draw.circle(range_overlay, (255, 255, 255, 45), (turret_range, turret_range), turret_range)
        pg.draw.circle(range_overlay, (255, 255, 255, 130), (turret_range, turret_range), turret_range, 2)
        screen.blit(range_overlay, (cursor_pos[0] - turret_range, cursor_pos[1] - turret_range))


def show_feedback(message):
    """Exibe uma mensagem temporaria no topo do mapa."""
    global feedback_message, feedback_message_time
    feedback_message = message
    feedback_message_time = pg.time.get_ticks()


def toggle_pause():
    """Alterna o pause durante a partida, descontando o tempo parado do spawn."""
    global paused, pause_started_at, level_start_time
    if game_state != "playing":
        return
    paused = not paused
    if paused:
        pause_started_at = pg.time.get_ticks()
    else:
        if pause_started_at is not None and level_start_time is not None:
            level_start_time += pg.time.get_ticks() - pause_started_at
        pause_started_at = None

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
    unlocked_count = level_config.get_level_config(level)["unlocked_towers"]
    return ordered_items[:unlocked_count]


def draw_hovered_turret_tooltip():
    """Mostra a explicação da torre quando o mouse passa sobre o botão."""
    mouse_pos = pg.mouse.get_pos()
    for index, (button, _turret_type) in enumerate(get_unlocked_turret_buttons(current_level)):
        if button.rect.collidepoint(mouse_pos):
            data = TURRET_DATA[index]
            draw_turret_tooltip(screen, cons, {
                "name": data["name"],
                "desc": data["desc"],
                "cost": data["cost"],
                "damage": data["damage"],
                "range": data["range"],
                "rect": button.rect,
            })
            break


def handle_turret_buttons():
    """Desenha os botões de torre e alterna o modo de posicionamento.

    Clicar num botão seleciona a torre; clicar no mesmo botão novamente
    cancela a seleção (desseleciona)."""
    for button, turret_type in get_unlocked_turret_buttons(current_level):
        if button.draw(screen):
            already_selected = (
                game_variables.placing_turrets
                and game_variables.current_turret_type == turret_type
            )
            if already_selected:
                game_variables.placing_turrets = False
                game_variables.current_turret_type = None
            else:
                game_variables.placing_turrets = True
                game_variables.current_turret_type = turret_type

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
    if pause.draw(screen):
        toggle_pause()
    
    if game_state == "dialogue_intro":
        # Desenha torres colocadas durante diálogo
        enemy_group.draw(screen)
        for enemy in enemy_group:
            enemy.draw_health_bar(screen)
        projectile_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)
        
        # Permite colocação de torres durante diálogo
        handle_turret_buttons()

        draw_tower_costs()

        if game_variables.placing_turrets:
            draw_placement_overlay()
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:
                game_variables.placing_turrets = False

        draw_ui(screen, cons, game_variables)

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

        handle_turret_buttons()

        draw_tower_costs()

        if game_variables.placing_turrets:
            draw_placement_overlay()
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:
                game_variables.placing_turrets = False

        draw_ui(screen, cons, game_variables)

    elif game_state == "playing":
        if not paused:
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
        for enemy in enemy_group:
            enemy.draw_health_bar(screen)
        projectile_group.draw(screen)
        for turret in turret_group:
            turret.draw(screen)
        
        handle_turret_buttons()

        draw_tower_costs()

        if game_variables.placing_turrets:
            draw_placement_overlay()
            cursor_rect = game_variables.current_turret_type.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[1] >= cons.UPPER_PANEL:
                screen.blit(game_variables.current_turret_type, cursor_rect)
            if pg.mouse.get_pressed()[2] == 1:
                game_variables.placing_turrets = False
        
        draw_ui(screen, cons, game_variables)
        footer_text = current_dialogue_data.get("enemy_intro", "")

        if paused:
            pause_overlay = pg.Surface((cons.SCREEN_WIDTH, cons.MAP_HEIGHT), pg.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 120))
            screen.blit(pause_overlay, (0, cons.UPPER_PANEL))
            font_pause = pg.font.Font(None, 72)
            pause_text = font_pause.render("PAUSADO", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + cons.MAP_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

    elif game_state == "victory_dialogue":
        footer_text = victory_message

        font_continue = pg.font.Font(None, 32)
        continue_text = font_continue.render("Clique para continuar", True, (255, 255, 0))
        continue_rect = continue_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + cons.MAP_HEIGHT // 2 + 70))
        screen.blit(continue_text, continue_rect)

        if current_level == level_config.TOTAL_LEVELS:
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

    # Tooltip da torre sob o mouse (por cima do mapa), nos estados com botões.
    if game_state in {"dialogue_intro", "waiting_for_start", "playing"}:
        draw_hovered_turret_tooltip()

    if feedback_message and pg.time.get_ticks() - feedback_message_time < 1500:
        font_feedback = pg.font.Font(None, 40)
        fb_text = font_feedback.render(feedback_message, True, (255, 80, 80))
        fb_rect = fb_text.get_rect(center=(cons.SCREEN_WIDTH // 2, cons.UPPER_PANEL + 40))
        screen.blit(fb_text, fb_rect)

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

        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            game_variables.placing_turrets = False

        if event.type == pg.KEYDOWN and event.key == pg.K_p and game_state == "playing":
            toggle_pause()

        if event.type == pg.KEYDOWN and event.key == pg.K_r and game_state == "game_over":
            apply_reset(current_level)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and game_state == "dialogue_intro":
            mouse_pos = pg.mouse.get_pos()
            # Se clicou no mapa, pode colocar torres
            if cons.UPPER_PANEL <= mouse_pos[1] < cons.UPPER_PANEL + cons.MAP_HEIGHT:
                if game_variables.placing_turrets:
                    placement_result = create_turret(
                        mouse_pos,
                        game_variables.current_turret_type,
                        cons,
                        world,
                        turret_group,
                        game_variables,
                        images,
                    )
                    if placement_result == "no_funds":
                        show_feedback("Moeda insuficiente!")
                    elif placement_result == "occupied":
                        show_feedback("Zona ja ocupada!")
            else:
                # Se clicou fora do mapa, avança diálogo
                if dialogue_index < len(intro_sequence):
                    dialogue_index += 1

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and game_state == "victory_dialogue":
            if current_level < level_config.TOTAL_LEVELS:
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
                    placement_result = create_turret(
                        mouse_pos,
                        game_variables.current_turret_type,
                        cons,
                        world,
                        turret_group,
                        game_variables,
                        images,
                    )
                    if placement_result == "no_funds":
                        show_feedback("Moeda insuficiente!")
                    elif placement_result == "occupied":
                        show_feedback("Zona ja ocupada!")
                else:
                    game_variables.selected_turret = select_turret(mouse_pos, cons, turret_group)
    
    pg.display.flip()

pg.quit()
