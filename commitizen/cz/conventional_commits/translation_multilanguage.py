from translate import Translator

FILENAME = "commitizen/cz/conventional_commits/.cache_multilanguage.txt"
MULTILANGUAGE = {}


def load_multilanguage():
    global MULTILANGUAGE
    MULTILANGUAGE = {}
    with open(FILENAME) as file:
        for line in file:
            if not line.strip():
                continue
            key, value = line.strip().split("=", 1)
            MULTILANGUAGE[key] = value

def generate_key(original_key, to_lang):
    return f"{original_key}_{to_lang}"

def save_multilanguage(key, value):
    if "\n" in value:
        value = value.replace("\n", "")
    with open(FILENAME, "a") as file:
        file.write(f"{key}={value}\n")

def translate_text(text, from_lang, to_lang):
    translator = Translator(from_lang=from_lang, to_lang=to_lang)
    translation = translator.translate(text)
    return translation

def translate_text_from_eng(text, to_lang, key):
    global MULTILANGUAGE
    key_generated = generate_key(key, to_lang)
    if not MULTILANGUAGE:
        load_multilanguage()
    if key_generated in MULTILANGUAGE:
        return MULTILANGUAGE[key_generated]
    else:
        if to_lang == "en":
            MULTILANGUAGE[key_generated] = text
            save_multilanguage(key_generated, MULTILANGUAGE[key_generated])
            return text
        MULTILANGUAGE[key_generated] = translate_text(text, "en", to_lang)
        save_multilanguage(key_generated, MULTILANGUAGE[key_generated])
        return MULTILANGUAGE[key_generated]
