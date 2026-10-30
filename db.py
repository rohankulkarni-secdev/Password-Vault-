import mysql.connector as sq

def setupDB():
    con = sq.connect(host='localhost', user='root', password='')
    curs=con.cursor()
    curs.execute("CREATE DATABASE IF NOT EXISTS vaultdb")
    curs.execute("USE vaultdb")
    curs.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(15) UNIQUE NOT NULL,
            password_hash VARBINARY(120) NOT NULL,
            kdf_salt VARBINARY(16) NOT NULL
        )
    """)
    curs.execute("""CREATE TABLE IF NOT EXISTS vault 
                (id INT AUTO_INCREMENT PRIMARY KEY, 
                user_id INT NOT NULL, 
                site VARCHAR(20) NOT NULL, 
                site_username VARCHAR(20) NOT NULL,
                password_encrypted TEXT NOT NULL, 
                FOREIGN KEY (user_id) REFERENCES users(id))""")
    con.commit()
    con.close()
    print("Database and Tables initialised")

def getCon():
    con=sq.connect(host='localhost', user='root',password='', database='vaultdb')
    curs=con.cursor()
    return con,curs

