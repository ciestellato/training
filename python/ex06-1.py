person = {
    'last_name' : 'utena',
    'first_name' : 'tenjo',
    'age' : 14,
    'city' : 'ootori'
}

print(person['last_name'])

fav_num = {
    'ami' : 20,
    'bae' : 100,
    'cherry' : 7,
    'dove' : 1,
    'emy' : 666
}

for name in fav_num:
    print(fav_num[name])
    print(fav_num.get(name))