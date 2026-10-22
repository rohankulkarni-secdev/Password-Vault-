import difflib
import bcrypt
from cryptography import fernet
import os
import crypto
import time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from db import getCon, setupDB

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
        username = input("Enter your username: ")

        try:
            curs.execute(f"""SELECT * FROM users WHERE username='{username}'""")
            pwd=input("Enter master password to access vault: ")
            row=curs.fetchone()
            print("Verifying Password Please Wait...")
            verify = verifyPassword(pwd,bytes(row[2]))
            if verify:
                
                print("Welcome!")
            else:
                print("Wrong Password!")

        except:       
            print("User Not Found, Try Again")
     
    

if __name__ == "__main__":
    main()