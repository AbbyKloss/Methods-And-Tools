import sqlite3
import random
import getpass
# import os

con = sqlite3.connect("testdb.db")
cur = con.cursor()

class User:
    def __init__(self, usr="", bool=False, id=0):
        self.name = usr
        self.Admin = bool
        self.ID = id
    
    def setName(self, str):
        self.name = str
    
    def setAdmin(self, bool):
        self.Admin = bool
    
    def setID(self, num):
        self.ID = num

    

# possibly prone to sql injection
# tried to do injection, it didn't work. there's a chance idk how to do it
# returns -1 on failure, 0 on success
def create_account():
    usern = input("Input Username:  ")
    passw = input("Input Password:  ")
    # pass2 = input("VERIFY PASSWORD: ")
    if (passw != input("Verify Password: ")):
        print("Passwords don't match")
        return -1
    cur.execute("select exists(select * from Users where Username=?)", (usern, ))
    if (int(cur.fetchone()[0])):
        print("Username already taken")
        return -1
    kill = 1
    # finds a random UserID
    while (kill):
        rand = random.randint(0, 99999)
        cur.execute("select exists(select * from Users where UserID=?)", (rand, ))
        kill = cur.fetchone()[0] # returns a 1 if userID is taken, 0 otherwise
    cur.execute("insert into Users values(?, ?, ?, 0)", (rand, usern, passw))
    con.commit()
    return 0

def help(code):
    if (code == 0): # 0 is not logged in
        print("Options: \n\tLogin\n\tCreate Account\n\tExit\n\tHelp")
    if (code == 1):
        print("Options: \n\texit \n\tidk lmao")

def login():
    # int = 0
    usern = input("INPUT USERNAME: ")
    passw = getpass.getpass("INPUT PASSWORD: ")
    cur.execute("select exists(select * from Users where Username=? AND Password=?)", (usern, passw))
    int = cur.fetchone()[0]
    if not (int):
        print("Wrong username or password")
        return int, None
    for row in cur.execute("select Admin, UserID from Users where Username=?", (usern, )):
        print("", end="") # do nothing command
    user = User(usern, row[0], row[1])
    return int, user

def searchByAuthor():
    author = input("INPUT AUTHOR NAME: ")
    for row in cur.execute("SELECT Title from Book where Author LIKE ?", (f"%{author}%", )):
        print(row[0])

# equivalent to a C main()
# starting the not definition code here

adminFlag = 0
logged_in = 0
kill = 0
user = 0

while not(logged_in):
    option = input("Guest % ").lower()
    if (option == "login"):
        logged_in, user = login()
    elif (option == "create account"):
        create_account()
    elif (option == "exit"):
        if (input("Exit? (Y/n): ").lower() == "y"):
            exit()
    elif (option == "help"):
        help(0)
    else:
        print(f"Unknown command: '{option}', try 'help'")

while(1):
    option = input(f"{user.name} % ").lower()
    if (option == "help"):
        help(1)
    elif (option == "exit"):
        if (input("Exit? (Y/n)").lower() == "y"):
            exit()
    else:
        print(f"Unknown command: '{option}', try 'help'")

con.close()
# print("done")