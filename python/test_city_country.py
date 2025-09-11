from ex11_1 import city_country

def test_ciry_country():
    city_and_country = city_country("santiago", "chile")
    assert city_and_country == "Santiago, Chile"