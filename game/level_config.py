"""Configuracao central das fases do jogo.

Centraliza, por fase: o mapa usado (imagem + JSON), o tipo de inimigo,
o maximo de inimigos da onda e quantas torres ficam desbloqueadas.

Para adicionar uma nova fase:
  1. Gere o mapa em tools/generate_maps.py (PNG + JSON).
  2. Acrescente uma entrada em LEVELS apontando para o nome do mapa.
  3. Adicione o dialogo correspondente em
     classes/character_impl/character_dialogue_data.json.
"""

LEVELS = {
    1: {"map": "firstLevel",  "enemy": "phishing",     "max_enemies": 8,  "unlocked_towers": 1},
    2: {"map": "secondLevel", "enemy": "keylogger",    "max_enemies": 12, "unlocked_towers": 2},
    3: {"map": "thirdLevel",  "enemy": "spyware",      "max_enemies": 15, "unlocked_towers": 3},
    4: {"map": "fourthLevel", "enemy": "malvertising", "max_enemies": 18, "unlocked_towers": 4},
    5: {"map": "fifthLevel",  "enemy": "databreach",   "max_enemies": 22, "unlocked_towers": 5},
}

TOTAL_LEVELS = max(LEVELS)

# Mapeia o tipo de inimigo para o atributo de imagem em LoadImages.
ENEMY_IMAGE_ATTR = {
    "phishing": "phishing_enemy",
    "keylogger": "keylogger_enemy",
    "spyware": "spyware_enemy",
    "malvertising": "malvertising_enemy",
    "databreach": "databreach_enemy",
}


def get_level_config(level):
    """Retorna a config da fase; cai na ultima fase se o nivel nao existir."""
    return LEVELS.get(level, LEVELS[TOTAL_LEVELS])


def map_image_path(level):
    return f"assets/images/levels/{get_level_config(level)['map']}.png"


def map_json_path(level):
    return f"assets/images/levels/{get_level_config(level)['map']}.json"


def enemy_image_attr(level):
    return ENEMY_IMAGE_ATTR.get(get_level_config(level)["enemy"], "phishing_enemy")
