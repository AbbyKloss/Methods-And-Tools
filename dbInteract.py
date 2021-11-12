import sqlite3
import random
# import os

con = sqlite3.connect("testdb.db")
cur = con.cursor()

adminFlag = 0
logged_in = 0

# possibly prone to sql injection
# tried to do injection, it didn't work. there's a chance idk how to do it
# returns -1 on failure, 0 on success
def create_account():
    usern = input("INPUT USERNAME:  ")
    passw = input("INPUT PASSWORD:  ")
    # pass2 = input("VERIFY PASSWORD: ")
    if (passw != input("VERIFY PASSWORD: ")):
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
    if (code == 0):
        print("Options: \n\tLogin,\n\tCreate Account,\n\tExit,\n\tHelp")

def login():
    int = 0
    usern = input("INPUT USERNAME: ")
    passw = input("INPUT PASSWORD: ")
    cur.execute("select exists(select * from Users where Username=? AND Password=?)", (usern, passw))
    int = cur.fetchone()[0]
    if not (int):
        print("Wrong username or password")
    return int

while not(logged_in):
    option = input("Guest % ").lower()
    if (option == "login"):
        logged_in = login()
    elif (option == "create account"):
        create_account()
    elif (option == "exit"):
        exit()
    elif (option == "help"):
        help(0)


strong = ""
author = input("INPUT AUTHOR NAME: ")
for row in cur.execute("SELECT Title from Book where Author LIKE ?", (f"%{author}%", )):
    strong += row[0]

print(strong)
con.close()
print("done")