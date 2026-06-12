import pygame as pg


def _wrap_text(font, text, max_width):
    """Quebra o texto em linhas que cabem em max_width pixels."""
    lines = []
    current = ""
    for word in text.split():
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_turret_tooltip(screen, cons, turret_info):
    """Desenha uma caixa explicativa perto de um botão de torre.

    turret_info: dict com 'name', 'desc', 'cost', 'damage', 'range' e o
    'rect' do botão sobre o qual o mouse está.
    """
    anchor = turret_info["rect"]
    font_title = pg.font.Font(None, 24)
    font_body = pg.font.Font(None, 20)

    padding = 10
    box_width = 240
    max_text_width = box_width - 2 * padding

    title_surface = font_title.render(turret_info["name"], True, (255, 215, 0))
    desc_lines = _wrap_text(font_body, turret_info["desc"], max_text_width)
    stats_text = (
        f"Custo: {turret_info['cost']}   "
        f"Dano: {turret_info['damage']}   "
        f"Alcance: {turret_info['range']}"
    )
    stats_lines = _wrap_text(font_body, stats_text, max_text_width)

    line_h = font_body.get_height() + 2
    box_height = (
        padding
        + title_surface.get_height() + 6
        + len(desc_lines) * line_h
        + 6
        + len(stats_lines) * line_h
        + padding
    )

    # Posiciona abaixo do botão; ajusta para não sair da tela.
    box_x = anchor.centerx - box_width // 2
    box_y = anchor.bottom + 22
    box_x = max(6, min(box_x, cons.SCREEN_WIDTH - box_width - 6))
    if box_y + box_height > cons.UPPER_PANEL + cons.MAP_HEIGHT:
        box_y = anchor.top - box_height - 8

    box_rect = pg.Rect(box_x, box_y, box_width, box_height)

    # Fundo semitransparente com borda.
    surface = pg.Surface((box_width, box_height), pg.SRCALPHA)
    surface.fill((18, 24, 30, 235))
    pg.draw.rect(surface, (255, 215, 0), surface.get_rect(), width=2, border_radius=8)
    screen.blit(surface, box_rect.topleft)

    y = box_y + padding
    screen.blit(title_surface, (box_x + padding, y))
    y += title_surface.get_height() + 6

    for line in desc_lines:
        text = font_body.render(line, True, (230, 230, 230))
        screen.blit(text, (box_x + padding, y))
        y += line_h

    y += 6
    for line in stats_lines:
        text = font_body.render(line, True, (140, 200, 255))
        screen.blit(text, (box_x + padding, y))
        y += line_h


def draw_ui(screen, cons, game_variables):
    font_small = pg.font.Font(None, 24)

    moeda_text = font_small.render(f"{game_variables.player_currency}", True, (255, 255, 255))
    screen.blit(moeda_text, (130, 33))

    vida_bar_width = 180
    vida_bar_height = 16
    vida_x = cons.SCREEN_WIDTH - 195
    vida_y = cons.SCREEN_HEIGHT - 600

    pg.draw.rect(screen, (100, 100, 100), (vida_x, vida_y, vida_bar_width, vida_bar_height))

    vida_percentage = game_variables.computer_health / game_variables.max_health
    vida_color = (0, 255, 0) if vida_percentage > 0.5 else (255, 165, 0) if vida_percentage > 0.2 else (255, 0, 0)
    pg.draw.rect(screen, vida_color, (vida_x, vida_y, int(vida_bar_width * vida_percentage), vida_bar_height))

    vida_text = font_small.render(
        f"Vida {game_variables.computer_health}/{game_variables.max_health}",
        True,
        (255, 255, 255),
    )
    screen.blit(vida_text, (vida_x, vida_y - 20))


def draw_dialogue_text(screen, speech, center=(450, 575), color=(255, 255, 255)):
    font = pg.font.Font(None, 28)
    max_width = 730
    line_spacing = 30
    max_lines = 4

    words = speech.replace("\n", " \n ").split()
    rendered_lines = []
    current_line = ""

    for word in words:
        if word == "\n":
            if current_line:
                rendered_lines.append(current_line)
                current_line = ""
            if len(rendered_lines) >= max_lines:
                break
            continue

        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                rendered_lines.append(current_line)
            current_line = word
            if len(rendered_lines) >= max_lines:
                break

    if current_line and len(rendered_lines) < max_lines:
        rendered_lines.append(current_line)

    block_height = len(rendered_lines) * line_spacing
    first_line_y = center[1] - (block_height // 2)

    for index, line in enumerate(rendered_lines):
        text = font.render(line, True, color)
        text_rect = text.get_rect(center=(center[0], first_line_y + index * line_spacing))
        screen.blit(text, text_rect)


def draw_dialogue_footer(screen, cons, y_position, texto_completo, superficie_avatar, superficie_footer):
    # Desenha o footer e avatar diretamente, sem scaling
    footer_rect = superficie_footer.get_rect(topleft=(0, y_position))
    screen.blit(superficie_footer, footer_rect.topleft)

    # Avatar centralizado verticalmente
    avatar_height = superficie_avatar.get_height()
    avatar_y = y_position + (cons.LOWER_PANEL - avatar_height) // 2
    screen.blit(superficie_avatar, (12, avatar_y))

    # Texto com quebra de linha automática, alinhado à direita do avatar
    padding = 15
    texto_x = 200  # Começa após o espaço do avatar
    texto_y = y_position + 20

    fonte = pg.font.Font(None, 24)
    distancia_linhas = fonte.get_height() + 4
    largura_maxima_texto = cons.SCREEN_WIDTH - texto_x - padding

    palavras = texto_completo.replace("\n", " \n ").split(" ") if texto_completo else []
    linha_atual = ""

    for palavra in palavras:
        if palavra == "\n":
            if linha_atual:
                text_surface = fonte.render(linha_atual.strip(), True, (255, 255, 255))
                screen.blit(text_surface, (texto_x, texto_y))
                texto_y += distancia_linhas
                linha_atual = ""
            continue

        test_linha = linha_atual + palavra + " "
        if fonte.size(test_linha)[0] < largura_maxima_texto:
            linha_atual = test_linha
        else:
            if linha_atual:
                text_surface = fonte.render(linha_atual.strip(), True, (255, 255, 255))
                screen.blit(text_surface, (texto_x, texto_y))
                texto_y += distancia_linhas
            linha_atual = palavra + " "

    if linha_atual:
        text_surface = fonte.render(linha_atual.strip(), True, (255, 255, 255))
        screen.blit(text_surface, (texto_x, texto_y))
