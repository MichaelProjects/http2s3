import base64
import os
import logging

from cryptography.fernet import Fernet


# Encrypt a message
def encrypt_message(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message)
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    try:
        decrypted_message = f.decrypt(encrypted_message)
        print(decrypted_message)
        return decrypted_message
    except Exception as e:
        print(f"COuld not decode: {e}")

    return encrypted_message
