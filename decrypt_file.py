import logging
import os
import argparse
from cryptography.fernet import Fernet


# Decrypt a message
def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


def load_file_to_binary(file_path):
    with open(file_path, 'rb') as file:
        return file.read()
    

def write_binary_to_file(file_path, binary_data):
    with open(file_path, 'wb') as file:
        file.write(binary_data)


def main():
    parser = argparse.ArgumentParser(description="Http2S3 decryption tool. Encryption key will be used from the env.")

    # Add the filename flag
    parser.add_argument('-f', '--file', type=str, required=True, help="Path to the file.")
    parser.add_argument('-o', '--output', type=str, required=False, help="Path to the output file.")

    # Parse the arguments
    args = parser.parse_args()

    if args.file == "" or args.file is None:
        print("No valid file provided.")
        parser.print_help()
        exit(1)

    filename = args.file.split("/")[-1]

    filename = f"output-{filename}"

    raw_data = load_file_to_binary(args.file)

    res = decrypt_message(raw_data, os.environ["encryption_key"])

    if args.output == "" or args.output is None:
        write_binary_to_file(filename, res)
    else:
        write_binary_to_file(args.output, res)

    print(f"Successfully decrypted {filename} to {args.output}")


if __name__ == "__main__":
    main()