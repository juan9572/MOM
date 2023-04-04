from base64 import b64encode, b64decode
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import json

def encrypt(plain_text, password):
    # Generamos siempre una salt aleatoria
    salt = get_random_bytes(AES.block_size)

    # Docs https://cryptobook.nakov.com/mac-and-key-derivation/scrypt
    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    # Docs https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
    cipher_config = AES.new(private_key, AES.MODE_GCM)

    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
    encryptedInfo = {
        'cipher_text': b64encode(cipher_text).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
        'tag': b64encode(tag).decode('utf-8')
    }
    return b64encode(bytes(str(encryptedInfo), 'ascii'))

def decrypt(enc_dict, password):
    enc_dict = json.loads(b64decode(enc_dict).decode('ascii').replace("'", '"'))
    salt = b64decode(enc_dict['salt'])
    cipher_text = b64decode(enc_dict['cipher_text'])
    nonce = b64decode(enc_dict['nonce'])
    tag = b64decode(enc_dict['tag'])

    private_key = hashlib.scrypt(
        password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)

    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

    decrypted = cipher.decrypt_and_verify(cipher_text, tag)

    return decrypted