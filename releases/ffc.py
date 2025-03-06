from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def encrypt_file(file_path, algorithm, key):
    with open(file_path, 'rb') as f:
        plaintext = f.read()

    if algorithm == 'XOR':
        ciphertext = xor_encrypt(plaintext, key)
    elif algorithm == 'AES':
        ciphertext = aes_encrypt(plaintext, key)
    else:
        raise ValueError("Unsupported algorithm")

    with open(file_path + '.enc', 'wb') as f:
        f.write(ciphertext)

def decrypt_file(file_path, algorithm, key):
    with open(file_path, 'rb') as f:
        ciphertext = f.read()

    if algorithm == 'XOR':
        plaintext = xor_decrypt(ciphertext, key)
    elif algorithm == 'AES':
        plaintext = aes_decrypt(ciphertext, key)
    else:
        raise ValueError("Unsupported algorithm")

    with open(file_path[:-4], 'wb') as f:
        f.write(plaintext)

def xor_encrypt(plaintext, key):
    return bytes([p ^ k for p, k in zip(plaintext, key * (len(plaintext) // len(key) + 1))])

def xor_decrypt(ciphertext, key):
    return xor_encrypt(ciphertext, key)

def aes_encrypt(plaintext, key):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext

def main():
    print("Welcome to ffc! Use help or ? for list of commands")
    while True:
        command = input(">>> ").strip().split()
        if not command:
            continue
        if command[0] in ['help', '?']:
            print("Commands:")
            print("c <file> <algorithm> - Encrypt file")
            print("ec <file> <algorithm> - Decrypt file")
            print("exit - Exit the program")
        elif command[0] == 'c':
            if len(command) != 3:
                print("Usage: c <file> <algorithm>")
                continue
            file_path = command[1]
            algorithm = command[2].upper()
            key = input("Enter key: ").encode()
            encrypt_file(file_path, algorithm, key)
            print(f"File {file_path} encrypted successfully.")
        elif command[0] == 'ec':
            if len(command) != 3:
                print("Usage: ec <file> <algorithm>")
                continue
            file_path = command[1]
            algorithm = command[2].upper()
            key = input("Enter key: ").encode()
            decrypt_file(file_path, algorithm, key)
            print(f"File {file_path} decrypted successfully.")
        elif command[0] == 'exit':
            break
        else:
            print("Unknown command. Use help or ? for list of commands.")

if __name__ == "__main__":
    main()
