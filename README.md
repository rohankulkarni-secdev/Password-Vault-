# 🔐 Python CLI Password Manager

A secure, local command-line password manager built in Python. It uses **MySQL** for data storage, **bcrypt** for user authentication, and **Fernet (AES-128)** for vault encryption. 

## 🚀 Features
- **User Authentication:** Secure registration and login using `bcrypt`.
- **Vault Management:** Add, view, search, and delete saved passwords.
- **Zero-Knowledge Encryption:** The master password is never stored. The encryption key is derived dynamically in memory and destroyed when the program exits.

## Future Feature:
- **Strength Checker:** Evaluates password complexity before saving.

## 🛡️ Security Architecture

This application separates **Hashing** (for logging in) from **Encryption** (for storing vault data). Here is how the flow works:

1. **User Registration:**
   - The master password is hashed using `bcrypt` and stored in the `users` table. `bcrypt` automatically handles salting and is intentionally slow to prevent brute-force attacks.
   - A random 16-byte salt (`os.urandom(16)`) is generated for the Key Derivation Function (KDF) and stored in the database.
2. **User Login & Key Derivation:**
   - The master password is verified against the `bcrypt` hash.
   - If successful, the plaintext master password is combined with the 16-byte salt and passed through `PBKDF2-HMAC-SHA256` (600,000 iterations) to derive a 32-byte Fernet encryption key.
   - **Crucial:** This key is held in RAM only. It is never stored in the database or on disk.
3. **Vault Operations:**
   - Passwords are encrypted using `Fernet` (which utilizes AES-128-CBC and HMAC-SHA256 for authenticity) before being inserted into the `vault_entries` table.
   - When viewing or searching, the ciphertext is decrypted in memory using the derived key.

## 🐛 Security Audits & Fixes

During development, I intentionally tested for vulnerabilities to understand how to secure the application.

- **SQL Injection (Found & Fixed):** 
  I initially constructed SQL queries using Python f-strings (e.g., `SELECT * FROM users WHERE username = '{user}'`). I successfully tested a SQL injection payload (`' OR '1'='1`) which bypassed authentication. I refactored the entire database layer to use **parameterized queries (`%s`)**, which ensures user input is treated strictly as data, not executable SQL code.
- **Data Leakage Prevention:** 
  I verified via MySQL that the `password_encrypted` column only stores unreadable Fernet ciphertext. Even if the database is compromised, the passwords remain secure without the in-memory key.

## 🛠️ Technology Stack
- **Language:** Python 3
- **Database:** MySQL (`mysql-connector-python`)
- **Cryptography:** `cryptography` (Fernet, PBKDF2HMAC), `bcrypt`

## 📦 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/password-manager.git
   cd password-manager



🗺️ Future Roadmap

□ Add password strength evaluation using zxcvbn.
□ Implement a password generator.
□ Add a GUI (Tkinter or PyQt) or Web Interface (Flask).
□ Implement auto-lock after X minutes of inactivity.