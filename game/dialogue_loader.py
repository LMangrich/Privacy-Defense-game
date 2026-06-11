import json


def load_all_dialogues(file_path):
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


def load_level_dialogue(all_dialogue_data, level):
    for level_data in all_dialogue_data["levels"]:
        if level_data["level"] == level:
            return level_data
    return None


def build_dialogue_sequence(level_dialogue):
    sequence = []
    sequence.extend(level_dialogue.get("intro_dialogues", []))
    sequence.extend(level_dialogue.get("tower_explanation", []))

    enemy_intro = level_dialogue.get("enemy_intro")
    if enemy_intro:
        sequence.append(enemy_intro)

    return sequence
