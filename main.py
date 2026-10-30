import difflib
import bcrypt
from cryptography import fernet
from cryptography.fernet import Fernet
import os
import base64
import crypto
import time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from db import getCon, setupDB


#custom function for key derivation. cryptography gives the raw math lib (PBKDF2HMAC), but we need to use it to process information, this function runs sha256 600,000 times, gives back exactly 32 bytes, wraps it in base64 so fernet accepts it. Salt is again for random stuff to be added to make it more random.


def derive_key(master_password, salt):
     kdf = PBKDF2HMAC(
          algorithm=hashes.SHA256(),
          length=32,
          salt = salt,
          iterations=600_600,
     )

     return base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))


def main():
    setupDB()
    print("============PASSWORD TOOL alpha 1.0.0============", end='\n')
    op=input("(1) Login / (2) Sign Up \n")
    if int(op)== 1:
        login()
    elif int(op)==2:
        signUp()
    else:
        print("Invalid Operation")


#-------- Hashing -------- #
#User Password Hashing:

def hashPassword(pwd):
        pwd = pwd.encode("UTF-8") #Encoding password for hashing algorithm 
        salt = bcrypt.gensalt(16) #Adding random string of characters before cryptographic algorithms act on it
        return bcrypt.hashpw(pwd, salt)

#using stored hash to verify password during login: 
def verifyPassword(pwd, passwordHash: bytes):
    pwd = pwd.encode("UTF-8")
    return bcrypt.checkpw(pwd, passwordHash)
              

#--------- Encryption --------- #


def signUp():
    con,curs = getCon()
    username=input("Enter new username: ")
    pwd=input("Enter your new master vault password: ")
    pwd= hashPassword(pwd)
    salt=os.urandom(16)
    curs.execute(
        "INSERT INTO users(username, password_hash, kdf_salt) VALUES (%s, %s, %s)",
        (username, pwd, salt)
    )    
    con.commit()
    con.close()
    print("User added, you can proceed to login.")
    time.sleep(1)
    login()

def login():
        con,curs = getCon()
        user = input("Enter your username: ")

        try:
            curs.execute(f"""SELECT * FROM users WHERE username='{user}'""")
            pwd=input("Enter master password to access vault: ")
            row=curs.fetchone()

            if not row:
                 print("User not found")
                 return
            else:
                print("Verifying Password Please Wait...")

            #row[2] is the bcrypt hash

            verify = verifyPassword(pwd,bytes(row[2]))

            if verify:
                print("Welcome!")
                db_salt = bytes(row[3])
                fernet_key = derive_key(pwd, db_salt)
                home(user, fernet_key)
            else:
                print("Wrong Password!")

        except Exception as e: print("Error:", e)      


def log(user, fernet_key):
     print("====== Log a Password ======")
     con,curs = getCon()

     site = input("Enter Name of Website: ")
     site_username = input("Enter Username: ")
     password = input("Enter Password to be Logged: ")

     curs.execute(f"""SELECT id FROM users WHERE username = '{user}'""")
     user_id = curs.fetchone()[0]
     print(user_id)
     f=Fernet(fernet_key) #initialising fernet key 

     #Encrypting password to store in sql db, but it comes out as bytes so we decode it to string (decode):
     password_encrypted = f.encrypt(password.encode()).decode()
     curs.execute("""INSERT INTO vault(user_id, site, site_username, password_encrypted) SELECT id, %s, %s, %s FROM users WHERE username = %s""", (site, site_username, password_encrypted, user))

     con.commit()
     con.close()
     print("Details added.")

def view(user, fernet_key):
     print("========= Displaying Vault Entries ========")
     con,curs = getCon()

     curs.execute(f"""SELECT id FROM users WHERE username = '{user}'""")
     user_id = curs.fetchone()[0]
     curs.execute(f"""SELECT id, site, site_username, password_encrypted FROM vault WHERE user_id = '{user_id}'""")
     rows = curs.fetchall()
     con.close()

     if not rows:
          print("\n")
          print("Vault is empty, log an entry")
          print("\n")
          return 1
     else:
          f=Fernet(fernet_key)
          for entry_id, site, site_username, cipherPwd in rows:
               #Decrypting encrypted password back to plain string to display
               plain_password = f.decrypt(cipherPwd.encode()).decode()
               print("-----------------------------------------")
               print(f"Entry: {entry_id}, Site: {site} | Username: {site_username} | Password: {plain_password}")
               print("-----------------------------------------")
               print("\n")

def delete(user):
     con,curs = getCon()
     curs.execute(f"SELECT id FROM users WHERE username = '{user}'")
     user_id = curs.fetchone()[0]
     entry_id = input("Enter ID of the entry to be deleted: ")
     
     try:
        curs.execute(f"""DELETE from VAULT where id = '{entry_id}' and user_id = '{user_id}'""")
        con.commit()
        con.close()
        print("Entry Deleted.")
     except:
            print("Entry does not exist.")


def search(user, fernet_key):
     con,curs = getCon()
     curs.execute(f"""SELECT id FROM users WHERE username = '{user}'""")
     user_id = curs.fetchone()[0]
     site = input("Enter site name: ")

     curs.execute(f"""SELECT id, site, site_username, password_encrypted FROM vault WHERE user_id = '{user_id}' AND site = '{site}'""")
     rows = curs.fetchall()
     con.close()
     
     if not rows:
        print("\n")
        print("Not Found")
        print("\n")
        return 1
     
     else:
        f=Fernet(fernet_key)
        for entry_id, site, site_username, cipherPwd in rows:
            #Decrypting encrypted password back to plain string to display
            plain_password = f.decrypt(cipherPwd.encode()).decode()
            print("-----------------------------------------")
            print(f"Entry: {entry_id}, Site: {site} | Username: {site_username} | Password: {plain_password}")
            print("-----------------------------------------")
            print("\n")    


def home(user, fernet_key):
     print("============ Choose Operation: ============\n")
     while True:
        print("(1) Log a password \n(2) View vault \n(3) Delete an entry \n(4) Search \n(5) Exit")
        inp = int(input("Enter an operation: "))
        if inp == 1:
            log(user, fernet_key)
        elif inp == 2:
            view(user, fernet_key)
        elif inp == 3:
            delete(user)
        elif inp == 4:
            search(user, fernet_key)
        elif inp == 5:
            print("Logging out... encryption key will be destroyed.")
            time.sleep(1)
            break
        else: 
            print("Invalid Input")
    


main()