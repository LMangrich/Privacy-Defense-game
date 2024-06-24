
def split_speech_into_lines(speech):
    speech_words_queue = speech.split(" ")
    # draw first character_impl

    response = {
        "first_line": "",
        "second_line": "",
        "third_line": "",
        "has_first_line": False,
        "has_second_line": False,
        "has_third_line": False,
    }

    while(len(response["first_line"]) < 50 and len(speech_words_queue) > 0):
        response["has_first_line"] = True
        response["first_line"] +=  (speech_words_queue.pop(0) + " ")

    while(len(response["second_line"]) < 50 and len(speech_words_queue) > 0):
        response["has_second_line"] = True
        response["second_line"] +=  (speech_words_queue.pop(0) + " ")

    while(len(response["third_line"]) < 50 and len(speech_words_queue) > 0):
        response["has_third_line"] = True
        response["third_line"] += (speech_words_queue.pop(0) + " ")

    return response