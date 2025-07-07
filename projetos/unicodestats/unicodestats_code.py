def unicodestats_characters(file_path):
    file = open(f'{file_path}', mode='r+', encoding='utf-8')
    characters_dict = {}

    for line in file:
        lower_line = line.lower().strip()
        characters = list(lower_line)
        for character in characters:
            n = characters_dict.get(character, 0) + 1
            characters_dict[character] = n

    return characters_dict