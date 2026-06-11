import pygame as pg


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
