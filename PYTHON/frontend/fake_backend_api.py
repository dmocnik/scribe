import random

users = {
    'dan': 'password',
    'notdan': 'notpassword'
}

def login(data):
    username = data['username']
    password = data['password']
    if users.get(username) == password:
        token = 'this_is_a_token_' + str(random.randint(0, 100))
        return (200, {'token': token})
    else:
        return (401, None)