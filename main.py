import sqlite3
import os
import string
import secrets
from cryptography.fernet import Fernet
import pyperclip

KEY_FILE = "secret.key"
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as key_file:
    KEY = key_file.read()
cipher = Fernet(KEY)

conn = sqlite3.connect("main.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL,
    field TEXT NOT NULL,
    value TEXT NOT NULL
)
""")
conn.commit()

def add_credential(identifier, field, value):
    encrypted_value = cipher.encrypt(value.encode())
    cursor.execute("INSERT INTO credentials (identifier, field, value) VALUES (?, ?, ?)",
                   (identifier, field, encrypted_value))
    conn.commit()
    print("Credential saved successfully!")

def get_credential(identifier, field):
    cursor.execute("SELECT value FROM credentials WHERE identifier = ? AND field = ?", (identifier, field))
    result = cursor.fetchone()
    if result:
        encrypted_value = result[0]
        value = cipher.decrypt(encrypted_value).decode()
        print(f"{field}: {value}")
        pyperclip.copy(value)
        print(f"{field} copied to clipboard.")
    else:
        print("No credential found for this identifier and field.")

def list_credentials():
    cursor.execute("SELECT DISTINCT identifier FROM credentials")
    results = cursor.fetchall()
    if results:
        print("\nStored Credentials:")
        for row in results:
            print(f"{row[0]}")
        print()
    else:
        print("No credentials found.")

def generate_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    pyperclip.copy(password)
    print("Password copied to clipboard.")
    return password

def main():
    while True:
        command = input("Enter command: ")
        parts = command.split()
        if not parts:
            continue
        if parts[0] == "set" and len(parts) == 4:
            _, identifier, field, value = parts
            add_credential(identifier, field, value)
        elif parts[0] == "get" and len(parts) == 3:
            _, identifier, field = parts
            get_credential(identifier, field)
        elif parts[0] == "generate":
            print(generate_password())
        elif parts[0] == "list":
            list_credentials()
        elif command == "exit":
            break
        else:
            print("Invalid command format. Use:")
            print("  'set <identifier> <field> <value>' to store a credential")
            print("  'get <identifier> <field>' to retrieve a credential")
            print("  'list' to show all stored credentials")

if __name__ == "__main__":
    main()

conn.close()
