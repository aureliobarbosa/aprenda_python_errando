from unicodestats_code import unicodestats_characters


def test_valid_file(tmp_path):
    file_path = tmp_path / "testfile.txt"
    file_content = "Abc abc!\n123."
    file_path.write_text(file_content, encoding="utf-8")

    result = unicodestats_characters(file_path)
    assert result == {
        "a": 2,
        "b": 2,
        "c": 2,
        " ": 1,
        "!": 1,
        "1": 1,
        "2": 1,
        "3": 1,
        ".": 1,
    }


def test_empty_file(tmp_path):
    file_path = tmp_path / "emptyfile.txt"
    file_path.write_text("", encoding="utf-8")

    result = unicodestats_characters(file_path)
    assert result == {}