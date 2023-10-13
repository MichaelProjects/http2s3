import os
import logging

from cryptography.fernet import Fernet


def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load the saved key
def load_key():
    return os.environ["encryption_key"]




if __name__ == "__main__":
    generate_key()