import random


def generate_password():
    symbols = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    password = ''
    for symbol in range(6):
        password += random.choice(symbols)
    return password
