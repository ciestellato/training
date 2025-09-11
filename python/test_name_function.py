from name_function import get_formatted_name

def test_first_last_name():
    """'Janis Joplin'のような名前で動作するのか？"""
    formatted_name = get_formatted_name('janis', 'joplin')
    assert formatted_name == 'Janis Joplinn'
    
def test_first_last_name_chinese_chara():
    """'Janis Joplin'のような名前で動作するのか？"""
    formatted_name = get_formatted_name('janis', '鈴木')
    assert formatted_name == 'Janis 鈴木'