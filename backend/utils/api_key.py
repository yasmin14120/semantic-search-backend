from binascii import hexlify
import os


def generate_api_key():
    return hexlify(os.urandom(64)).decode()


def authenticate(home_key, strange_key):
    return home_key == strange_key
