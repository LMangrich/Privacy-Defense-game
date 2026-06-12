# Privacy Defense Game

Um jogo **Tower Defense** educativo sobre **privacidade e segurança digital**.
Defenda seu computador das ameaças cibernéticas (phishing, keylogger, spyware)
construindo torres que representam boas práticas de segurança: antivírus,
firewall, senha forte, filtro de e-mail, e mais.

Feito com **Python + Pygame**.

## Como jogar

- O jogo tem **5 níveis**, cada um com seu próprio mapa, um tipo de inimigo e novas torres desbloqueadas.
- Você começa com **100 de vida** e moeda para comprar torres.
- Passe o mouse sobre um botão de torre para ver uma breve explicação do que ela faz.
- A personagem **Letícia** explica os conceitos de privacidade durante os diálogos.

### Controles

- **Clique** em um botão de torre (no topo) para selecioná-la.
- **Clique** no mapa para posicionar a torre em uma zona válida.
- **Botão direito** do mouse cancela a colocação.
- **ENTER** inicia a onda de inimigos.
- **R** reinicia o nível após um game over.
- Clique para avançar diálogos e continuar entre os níveis.

## Requisitos

- **Python 3.10+** (testado no Python 3.14)
- **pygame-ce** (Pygame Community Edition)

> **Observação:** o pacote `pygame` clássico não possui versão pré-compilada
> para o Python 3.14. Use o `pygame-ce`, que é totalmente compatível com a
> mesma API (`import pygame`).

## Instalação

Clone o repositório e, na raiz do projeto, instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Como rodar

Execute a partir da **raiz do projeto** (a pasta `Privacy-Defense-game`):

```bash
python main.py
```

> O jogo usa caminhos relativos para carregar os assets, então é importante
> rodar a partir da pasta raiz do projeto.

## Estrutura do projeto

```
main.py                  → Loop principal e máquina de estados do jogo
util.py                  → Funções utilitárias
constants/               → Dimensões, FPS, tamanho dos tiles
classes/                 → Entidades do jogo (POO)
  buttons_impl/          → Botões da interface
  character_impl/        → Personagem e diálogos (textos em JSON)
  enemy_impl/            → Inimigos e seus dados
  projectile_impl/       → Projéteis das torres
  turret_impl/           → Torres e seus dados (alcance, dano, custo)
  world_impl/            → Mapa, waypoints e zonas de torre
game/                    → Lógica de jogo (gameplay, ui, diálogos)
initialize/              → Carregamento de imagens e variáveis iniciais
assets/images/           → Sprites (torres, inimigos, botões, mapa, níveis)
```

### Estados do jogo

```
dialogue_intro → waiting_for_start → playing → victory_dialogue
                                             ↘ game_over
```
