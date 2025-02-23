import sqlite3
import os
from cryptography.fernet import Fernet

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
    key TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

def add_credential(key, email, password):
    encrypted_password = cipher.encrypt(password.encode())
    cursor.execute("INSERT INTO credentials (key, email, password) VALUES (?, ?, ?)",
                   (key, email, encrypted_password))
    conn.commit()
    print("Credential saved successfully!")

def get_credential(key, field):
    cursor.execute("SELECT email, password FROM credentials WHERE key = ?", (key,))
    result = cursor.fetchone()
    if result:
        email, encrypted_password = result
        password = cipher.decrypt(encrypted_password).decode()
        if field == "em":
            print(f"Email: {email}")
        elif field == "pw":
            print(f"Password: {password}")
        else:
            print("Invalid field. Use 'em' for email or 'pw' for password.")
    else:
        print("No credentials found for this key.")

def main():
    while True:
        command = input("Enter command: ")
        parts = command.split()
        if len(parts) == 4 and parts[0] == "set":
            _, key, email, password = parts
            add_credential(key, email, password)
        elif len(parts) == 3 and parts[0] == "get":
            _, key, field = parts
            get_credential(key, field)
        elif command == "exit":
            break
        else:
            print("Invalid command format. Use: \n'set <key> <email> <password>' to store credentials \n'get <key> em' to get email \n'get <key> pw' to get password")

if __name__ == "__main__":
    main()

conn.close()
