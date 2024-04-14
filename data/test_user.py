from requests import get, post, delete, put

print(get('http://localhost:5000/api/v2/users').json())
print(get('http://localhost:5000/api/v2/users/1').json())
print(get('http://localhost:5000/api/v2/users/10').json())
print(get('http://localhost:5000/api/v2/users/q').json())

print(post('http://localhost:5000/api/v2/users', json={'surname': 'pass',
                                                       'name': 'job',
                                                       'age': 1,
                                                       'position': 'gamer',
                                                       'speciality': 'gamer',
                                                       'address': 'gamer st',
                                                       'email': 'gamer@ya.ru',
                                                       'modified_date': '1',
                                                       'city_from': 'msc'}).json())

print(delete(f'http://localhost:5000/api/v2/users/4').json())
