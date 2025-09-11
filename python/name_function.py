def get_formatted_name(first, last):
    """フォーマットされたフルネームを返す"""
    full_name = f"{first} {last}"
    return full_name.title()

name = get_formatted_name("first", "last")
print(name == "First Last")