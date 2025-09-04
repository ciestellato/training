# 6-7.
people = [
    {"name": "田中太郎", "email": "tanaka.taro@example.com", "phone": "090-1234-5678"},
    {"name": "佐藤花子", "email": "sato.hanako@example.com", "phone": "080-2345-6789"},
    {"name": "鈴木一郎", "email": "suzuki.ichiro@example.com", "phone": "070-3456-7890"}
]
for person in people:
    for item in person.items():
        print(item)

# 6-8.
pets = [
    {"animal": "dog", "owner": "田中太郎"},
    {"animal": "cat", "owner": "佐藤花子"},
    {"animal": "parrot", "owner": "鈴木一郎"},
    {"animal": "rabbit", "owner": "高橋美咲"},
    {"animal": "hamster", "owner": "山本健太"}
]
for pet in pets:
    print(pet.get("owner"), "が、飼っているのは", pet.get("animal"))

# 6-9.
favorite_places = [
    {"name": "田中太郎", "place": ["京都", "大阪", "奈良"]},
    {"name": "佐藤花子", "place": ["沖縄", "熊本"]},
    {"name": "鈴木一郎", "place": ["箱根", "大分", "群馬"]},
    {"name": "高橋美咲", "place": ["軽井沢"]},
    {"name": "山本健太", "place": ["北海道", "香川"]}
]
for data in favorite_places:
    print(data.get("name"), "が好きな場所は、下記の通りです。")
    for place in data.get("place"):
        print("・", place)

# 6-10.好きな数字
favorite_numbers = {
	"田中":[2,4,6],
	"佐藤":[1,8],
	"高橋":[7],
}
for key, values in favorite_numbers.items():
    print(key, end=" : ")
    for value in values:
        print(value, end=",")
    print()

# 6-11.都市
cities = {
    "San Diego": {
        "country": "アメリカ",
        "population": 1400000,
        "feature": "温暖な気候と美しい海岸線"
    },
    "Austin": {
        "country": "アメリカ",
        "population": 1000000,
        "feature": "音楽とテクノロジーの街"
    },
    "Miami": {
        "country": "アメリカ",
        "population": 470000,
        "feature": "熱帯気候と多文化な雰囲気"
    }
}
for city, values in cities.items():
    print(city, "の特徴")
    print(f"{values['country']}にあり、人口は約{values['population']}名。特徴は{values['feature']}")