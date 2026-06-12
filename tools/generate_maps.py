"""Gerador de mapas para o Privacy Defense.

O jogo nao renderiza tiles: ele apenas desenha uma imagem PNG pronta do mapa
e usa o JSON para os waypoints (caminho dos inimigos) e zonas de torre.

Este script desenha mapas novos no mesmo estilo visual do firstLevel.png
(fundo escuro esverdeado + caminho cinza claro + computador no fim) e gera
o JSON correspondente (waypoints + "Zona de torres").

Uso:
    python tools/generate_maps.py

As coordenadas usadas aqui sao relativas ao mapa (0,0 = canto superior
esquerdo da imagem de 960x624). O jogo soma UPPER_PANEL ao desenhar.
"""

import json
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # permite rodar sem janela

import pygame as pg

# ---- Dimensoes do mapa (espelham constants.py) ----
TILE_SIZE = 48
COLUMNS = 20
ROWS = 13
MAP_WIDTH = TILE_SIZE * COLUMNS   # 960
MAP_HEIGHT = TILE_SIZE * ROWS     # 624

LEVELS_DIR = os.path.join("assets", "images", "levels")

# ---- Paleta (amostrada do firstLevel.png) ----
COLOR_BG = (34, 46, 42)          # fundo escuro esverdeado
COLOR_BG_DEEP = (24, 34, 31)     # vinheta dos cantos
COLOR_CIRCUIT = (52, 70, 64)     # linhas de circuito do fundo
COLOR_CIRCUIT_NODE = (70, 96, 88)
COLOR_PATH = (96, 106, 101)      # caminho cinza claro
COLOR_PATH_EDGE = (70, 80, 76)   # borda do caminho
COLOR_PATH_DASH = (130, 142, 136)  # linha central tracejada
COLOR_ZONE = (60, 120, 200)      # marcador de zona de torre (tomada azul)
COLOR_ZONE_DARK = (28, 56, 104)

PATH_WIDTH = 84                  # largura do caminho em pixels

# ---- Definicao das fases ----
# Cada caminho comeca numa borda (inimigo "entra de fora") e termina no
# computador. y relativo ao topo do mapa. "accent" da identidade visual
# propria a cada fase (portal de entrada, brilho do caminho).
LEVELS = {
    "secondLevel": {
        "accent": (70, 150, 230),     # azul
        "waypoints": [
            (-20, 110), (840, 110), (840, 300), (120, 300),
            (120, 510), (880, 510),
        ],
    },
    "thirdLevel": {
        "accent": (80, 200, 130),     # verde
        "waypoints": [
            (480, -20), (480, 150), (130, 150), (130, 330),
            (820, 330), (820, 500), (470, 500),
        ],
    },
    "fourthLevel": {
        "accent": (235, 165, 70),     # laranja
        "waypoints": [
            (-20, 80), (880, 80), (880, 540), (130, 540),
            (130, 230), (740, 230), (740, 430),
        ],
    },
    "fifthLevel": {
        "accent": (220, 80, 110),     # vermelho/rosa
        "waypoints": [
            (-20, 90), (760, 90), (760, 250), (150, 250),
            (150, 400), (820, 400), (820, 540), (320, 540),
        ],
    },
}


def point_to_segment_distance(px, py, ax, ay, bx, by):
    """Distancia do ponto (px,py) ao segmento AB."""
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return math.hypot(apx, apy)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab_len_sq))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(px - cx, py - cy)


def distance_to_path(px, py, waypoints):
    return min(
        point_to_segment_distance(px, py, *waypoints[i], *waypoints[i + 1])
        for i in range(len(waypoints) - 1)
    )


def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_background(surface, accent):
    surface.fill(COLOR_BG)

    # Padrao de placa de circuito: linhas finas + nos nas intersecoes.
    step = 48
    for x in range(step, MAP_WIDTH, step):
        pg.draw.line(surface, COLOR_CIRCUIT, (x, 0), (x, MAP_HEIGHT), 1)
    for y in range(step, MAP_HEIGHT, step):
        pg.draw.line(surface, COLOR_CIRCUIT, (0, y), (MAP_WIDTH, y), 1)
    for x in range(step, MAP_WIDTH, step):
        for y in range(step, MAP_HEIGHT, step):
            if (x // step + y // step) % 3 == 0:
                pg.draw.circle(surface, COLOR_CIRCUIT_NODE, (x, y), 3)
                pg.draw.circle(surface, COLOR_BG, (x, y), 1)

    # Vinheta: escurece sutilmente as bordas com um leve tom do accent.
    vignette = pg.Surface((MAP_WIDTH, MAP_HEIGHT), pg.SRCALPHA)
    edge = _lerp(COLOR_BG_DEEP, accent, 0.12)
    border = 90
    for i in range(border):
        alpha = int(150 * (1 - i / border))
        pg.draw.rect(
            vignette, (*edge, alpha),
            pg.Rect(i, i, MAP_WIDTH - 2 * i, MAP_HEIGHT - 2 * i), 1,
        )
    surface.blit(vignette, (0, 0))


def _draw_dashed_polyline(surface, color, pts, width, dash=26, gap=22):
    """Desenha uma linha tracejada ao longo da polilinha (direcao do caminho)."""
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        seg_len = math.hypot(bx - ax, by - ay)
        if seg_len == 0:
            continue
        dx, dy = (bx - ax) / seg_len, (by - ay) / seg_len
        dist = 0.0
        while dist < seg_len:
            start = dist
            end = min(dist + dash, seg_len)
            sx, sy = ax + dx * start, ay + dy * start
            ex, ey = ax + dx * end, ay + dy * end
            pg.draw.line(surface, color, (sx, sy), (ex, ey), width)
            dist += dash + gap


def draw_path(surface, waypoints, accent):
    half = PATH_WIDTH // 2
    pts = [(int(x), int(y)) for x, y in waypoints]

    # 1. Brilho externo suave na cor de destaque (varias camadas com alpha).
    glow = pg.Surface((MAP_WIDTH, MAP_HEIGHT), pg.SRCALPHA)
    for extra, alpha in ((22, 30), (12, 45)):
        w = PATH_WIDTH + extra
        pg.draw.lines(glow, (*accent, alpha), False, pts, w)
        for x, y in pts:
            pg.draw.circle(glow, (*accent, alpha), (x, y), w // 2)
    surface.blit(glow, (0, 0))

    # 2. Borda do caminho.
    pg.draw.lines(surface, COLOR_PATH_EDGE, False, pts, PATH_WIDTH + 6)
    for x, y in pts:
        pg.draw.circle(surface, COLOR_PATH_EDGE, (x, y), half + 3)

    # 3. Caminho principal.
    pg.draw.lines(surface, COLOR_PATH, False, pts, PATH_WIDTH)
    for x, y in pts:
        pg.draw.circle(surface, COLOR_PATH, (x, y), half)

    # 4. Linha central tracejada indicando a direcao do percurso.
    _draw_dashed_polyline(surface, COLOR_PATH_DASH, pts, 4)


def draw_entry_portal(surface, waypoints, accent):
    """Marca o ponto de entrada dos inimigos com um portal brilhante."""
    # primeiro waypoint pode estar fora da tela (-20); usa o segundo como apoio
    ax, ay = waypoints[0]
    bx, by = waypoints[1]
    # posiciona o portal logo dentro do mapa, sobre o caminho de entrada
    px = min(max(ax, 30), MAP_WIDTH - 30)
    py = min(max(ay, 30), MAP_HEIGHT - 30)

    portal = pg.Surface((MAP_WIDTH, MAP_HEIGHT), pg.SRCALPHA)
    for radius, alpha in ((46, 60), (34, 90), (24, 140)):
        pg.draw.circle(portal, (*accent, alpha), (int(px), int(py)), radius)
    surface.blit(portal, (0, 0))
    pg.draw.circle(surface, accent, (int(px), int(py)), 18, 3)
    pg.draw.circle(surface, _lerp(accent, (255, 255, 255), 0.4),
                   (int(px), int(py)), 9)


def draw_computer(surface, position):
    """Desenha um computador/laptop estilizado (o alvo a ser protegido)."""
    cx, cy = int(position[0]), int(position[1])
    # mantem dentro da imagem
    cx = max(80, min(MAP_WIDTH - 80, cx))
    cy = max(70, min(MAP_HEIGHT - 80, cy))

    # brilho de "alvo protegido" ao redor
    glow = pg.Surface((MAP_WIDTH, MAP_HEIGHT), pg.SRCALPHA)
    for radius, alpha in ((96, 30), (74, 45)):
        pg.draw.circle(glow, (120, 200, 230, alpha), (cx, cy - 4), radius)
    surface.blit(glow, (0, 0))

    body = pg.Rect(0, 0, 132, 90)
    body.center = (cx, cy)
    # carcaca da tela
    pg.draw.rect(surface, (44, 52, 62), body, border_radius=10)
    pg.draw.rect(surface, (150, 160, 175), body, width=4, border_radius=10)
    # tela com leve degrade (azul claro -> azul)
    screen_inner = body.inflate(-22, -22)
    pg.draw.rect(surface, (110, 180, 225), screen_inner, border_radius=5)
    pg.draw.rect(surface, (140, 205, 240),
                 screen_inner.inflate(0, -screen_inner.height // 2)
                 .move(0, -screen_inner.height // 4), border_radius=5)

    # icone de cadeado/escudo na tela
    shield_w, shield_h = 26, 30
    sx = cx - shield_w // 2
    sy = screen_inner.centery - shield_h // 2
    shield = [
        (sx + shield_w // 2, sy),
        (sx + shield_w, sy + 6),
        (sx + shield_w, sy + shield_h - 12),
        (sx + shield_w // 2, sy + shield_h),
        (sx, sy + shield_h - 12),
        (sx, sy + 6),
    ]
    pg.draw.polygon(surface, (40, 70, 110), shield)
    pg.draw.polygon(surface, (230, 240, 250), shield, 2)
    pg.draw.circle(surface, (230, 240, 250),
                   (cx, screen_inner.centery - 1), 4)
    pg.draw.rect(surface, (230, 240, 250),
                 pg.Rect(cx - 2, screen_inner.centery - 1, 4, 9))

    # base/teclado
    base = pg.Rect(0, 0, 156, 16)
    base.midtop = (cx, body.bottom)
    pg.draw.rect(surface, (170, 180, 195), base, border_radius=5)
    pg.draw.rect(surface, (120, 130, 145), base, width=2, border_radius=5)


def generate_tower_zones(waypoints, max_zones=16):
    """Gera pontos de zona de torre proximos ao caminho (mas nao em cima)."""
    zones = []
    min_dist, max_dist = 58, 96
    margin = 36            # mantem o marcador longe da borda da imagem
    sep = 100             # distancia minima entre zonas
    spacing = 100         # grade de candidatos
    for gy in range(spacing // 2, MAP_HEIGHT, spacing):
        for gx in range(spacing // 2, MAP_WIDTH, spacing):
            if not (margin <= gx <= MAP_WIDTH - margin):
                continue
            if not (margin <= gy <= MAP_HEIGHT - margin):
                continue
            d = distance_to_path(gx, gy, waypoints)
            if min_dist <= d <= max_dist:
                if all(math.hypot(gx - zx, gy - zy) > sep for zx, zy in zones):
                    zones.append((gx, gy))
                    if len(zones) >= max_zones:
                        return zones
    return zones


def draw_zone_markers(surface, zones):
    """Marcadores de tomada indicando onde da para construir torres."""
    for zx, zy in zones:
        cx, cy = int(zx), int(zy)
        # leve halo para destacar do fundo
        halo = pg.Surface((MAP_WIDTH, MAP_HEIGHT), pg.SRCALPHA)
        pg.draw.circle(halo, (*COLOR_ZONE, 35), (cx, cy), 28)
        surface.blit(halo, (0, 0))

        rect = pg.Rect(0, 0, 36, 36)
        rect.center = (cx, cy)
        pg.draw.rect(surface, COLOR_ZONE_DARK, rect, border_radius=8)
        pg.draw.rect(surface, COLOR_ZONE, rect, width=3, border_radius=8)
        # dois "furos" de tomada
        pg.draw.circle(surface, COLOR_ZONE, (cx - 7, cy - 2), 3)
        pg.draw.circle(surface, COLOR_ZONE, (cx + 7, cy - 2), 3)
        pg.draw.rect(surface, COLOR_ZONE, pg.Rect(cx - 2, cy + 4, 4, 6),
                     border_radius=2)


def build_level_json(waypoints, zones):
    """Monta o dicionario no formato esperado por World.process_data."""
    waypoint_objects = [
        {
            "height": 0, "id": i + 1, "name": "", "opacity": 1,
            "rotation": 0, "type": "", "visible": True, "width": 0,
            # clamp para dentro do mapa (o ponto de entrada fica em -20)
            "x": max(0, min(MAP_WIDTH, float(x))),
            "y": max(0, min(MAP_HEIGHT, float(y))),
        }
        for i, (x, y) in enumerate(waypoints)
    ]

    zone_objects = [
        {
            "height": 0, "id": 100 + i, "name": "", "opacity": 1,
            "rotation": 0, "type": "", "visible": True, "width": 0,
            "x": float(x), "y": float(y),
        }
        for i, (x, y) in enumerate(zones)
    ]

    return {
        "compressionlevel": -1,
        "height": ROWS,
        "infinite": False,
        "layers": [
            {
                "draworder": "topdown", "id": 4, "name": "Zona de torres",
                "objects": zone_objects, "opacity": 1, "type": "objectgroup",
                "visible": True, "x": 0, "y": 0,
            },
            {
                "draworder": "topdown", "id": 3, "name": "waypoints",
                "objects": waypoint_objects, "opacity": 1, "type": "objectgroup",
                "visible": True, "x": 0, "y": 0,
            },
        ],
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "tileheight": TILE_SIZE,
        "tilewidth": TILE_SIZE,
        "type": "map",
        "version": "1.10",
        "width": COLUMNS,
    }


def generate_level(name, config):
    waypoints = config["waypoints"]
    accent = config["accent"]

    surface = pg.Surface((MAP_WIDTH, MAP_HEIGHT), pg.SRCALPHA)
    draw_background(surface, accent)
    draw_path(surface, waypoints, accent)
    draw_entry_portal(surface, waypoints, accent)

    zones = generate_tower_zones(waypoints)
    draw_zone_markers(surface, zones)
    draw_computer(surface, waypoints[-1])

    png_path = os.path.join(LEVELS_DIR, f"{name}.png")
    json_path = os.path.join(LEVELS_DIR, f"{name}.json")

    pg.image.save(surface, png_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(build_level_json(waypoints, zones), f, ensure_ascii=False, indent=1)

    print(f"[ok] {name}: {len(waypoints)} waypoints, {len(zones)} zonas -> {png_path}")


def main():
    pg.init()
    os.makedirs(LEVELS_DIR, exist_ok=True)
    for name, config in LEVELS.items():
        generate_level(name, config)
    pg.quit()


if __name__ == "__main__":
    main()
