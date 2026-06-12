import pygame as pg

from constants.constants import DEBUG
from classes.enemy_impl.enemy import Enemy
from classes.enemy_impl.enemy_data import ENEMY_DATA
from classes.turret_impl.turret import Turret
from classes.turret_impl.turret_data import TURRET_DATA
from game.level_config import get_level_config, enemy_image_attr


def on_enemy_reach_end(game_variables):
    if hasattr(game_variables, "take_damage"):
        game_variables.take_damage(20)
    else:
        game_variables.computer_health = max(0, game_variables.computer_health - 20)


def create_turret(mouse_pos, turret_type, cons, world, turret_group, game_variables, images):
    # 1. Transform mouse click position directly to map-space coordinates
    map_click_x = mouse_pos[0]
    map_click_y = mouse_pos[1] - cons.UPPER_PANEL

    selected_zone = None
    CLICK_RADIUS = 24  

    # 2. Match click against map-relative zones
    for zone in world.tower_zones:
        dx = map_click_x - zone.centerx
        dy = map_click_y - zone.centery
        if (dx * dx + dy * dy) <= CLICK_RADIUS * CLICK_RADIUS:
            selected_zone = zone
            break

    if selected_zone is None:
        return "no_zone"

    # 3. Derive tile indices cleanly from map-relative space
    mouse_tile_x = int(selected_zone.centerx // cons.TILE_SIZE)
    mouse_tile_y = int(selected_zone.centery // cons.TILE_SIZE)

    if DEBUG:
        print(f"[DEBUG] Zone Found! Map-relative Center: ({selected_zone.centerx}, {selected_zone.centery}) | Grid Tile: ({mouse_tile_x}, {mouse_tile_y})")

    # 4. Check occupancy
    zone_occupied = any(
        (turret.tile_x, turret.tile_y) == (mouse_tile_x, mouse_tile_y)
        for turret in turret_group
    )
    if zone_occupied:
        if DEBUG:
            print(f"[DEBUG] Placement blocked: Tile ({mouse_tile_x}, {mouse_tile_y}) occupied.")
        return "occupied"

    # 5. Check currency - map turret type to data index
    turret_type_map = {
        images.cursor_get_antivirus: 0,
        images.cursor_get_firewall: 1,
        images.cursor_get_strong_password: 2,
        images.cursor_get_filter_email: 3,
        images.cursor_get_usb_unknown: 4,
        images.cursor_get_unsafe_download: 5,
        images.cursor_get_adblock: 6,
        images.cursor_get_change_password: 7,
    }
    turret_data_index = turret_type_map.get(turret_type, 0)
    turret_cost = TURRET_DATA[turret_data_index]["cost"]
    
    if game_variables.player_currency < turret_cost:
        if DEBUG:
            print(f"[DEBUG] Insufficient funds: Needs {turret_cost}, Player has {game_variables.player_currency}")
        return "no_funds"

    # 6. Instantiate turret
    new_turret = Turret(turret_type, mouse_tile_x, mouse_tile_y, cons, images, game_variables, turret_data_index)
    turret_group.add(new_turret)
    game_variables.player_currency -= turret_cost
    if DEBUG:
        print(f"[DEBUG] Turret placed at grid tile ({mouse_tile_x}, {mouse_tile_y})")
    return "placed"

    
def select_turret(mouse_pos, cons, turret_group):
    mouse_tile_x = mouse_pos[0] // cons.TILE_SIZE
    mouse_tile_y = (mouse_pos[1] - cons.UPPER_PANEL) // cons.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret
    return None


def clear_selection(turret_group):
    for turret in turret_group:
        turret.selected = False


def spawn_enemy_wave(current_level, level_start_time, enemy_wave_spawned, images, world, enemy_group, game_variables):
    # Config da fase (mapa, inimigo, máximo de inimigos, torres)
    config = get_level_config(current_level)
    max_enemies = config["max_enemies"]
    enemy_type = config["enemy"]
    enemy_image = getattr(images, enemy_image_attr(current_level))

    current_time = pg.time.get_ticks()
    time_elapsed = (current_time - level_start_time) / 1000.0

    if time_elapsed < 1.0:
        enemies_to_spawn = min(2, int(time_elapsed * 2) + 1)
    else:
        enemies_to_spawn = 2 + int((time_elapsed - 1.0) / 3.0) + 1

    # Limita ao máximo de inimigos do nível
    enemies_to_spawn = min(enemies_to_spawn, max_enemies)

    while enemy_wave_spawned < enemies_to_spawn:
        enemy_health = ENEMY_DATA[enemy_type]["health"]
        enemy_speed = ENEMY_DATA[enemy_type]["speed"]
        enemy = Enemy(world.waypoints, enemy_image, health=enemy_health, on_reach_end=lambda: on_enemy_reach_end(game_variables), speed=enemy_speed)
        enemy_group.add(enemy)
        enemy_wave_spawned += 1

    return enemy_wave_spawned


def reset_level(current_level, game_variables, turret_group, projectile_group, enemy_group, load_level_dialogue_fn, all_dialogue_data):
    turret_group.empty()
    projectile_group.empty()
    enemy_group.empty()

    game_variables.computer_health = 100
    game_variables.player_currency = 200
    game_variables.placing_turrets = False
    game_variables.selected_turret = None

    return {
        "game_state": "dialogue_intro",
        "dialogue_index": 0,
        "enemy_wave_spawned": 0,
        "showing_game_over": False,
        "game_over_message": "",
        "current_dialogue_data": load_level_dialogue_fn(all_dialogue_data, current_level),
        "level_start_time": None,
    }
