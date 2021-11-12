import sqlite3
import random
import getpass
# import os

con = sqlite3.connect("testdb.db")
cur = con.cursor()

class User:
    def __init__(self, usr="Guest", bool=False, id=0):
        self.name = usr
        self.Admin = bool
        self.ID = id
    
    def setName(self, str):
        self.name = str
    
    def setAdmin(self, bool):
        self.Admin = bool
    
    def setID(self, num):
        self.ID = num

class Driver:
    def __init__(self):
        self.user = User()
        self.logged_in = 0
        self.help_code = 0

    # possibly prone to sql injection
    # tried to do injection, it didn't work. there's a chance idk how to do it
    # returns -1 on failure, 0 on success
    def create_account(self):
        usern = input("Input Username:  ")
        passw = getpass.getpass("Input Password:  ")
        # pass2 = input("VERIFY PASSWORD: ")
        if (passw != getpass.getpass("Verify Password: ")):
            print("Passwords don't match")
            return
        cur.execute("select exists(select * from Users where Username=?)", (usern, ))
        if (int(cur.fetchone()[0])):
            print("Username already taken")
            return
        kill = 1
        # finds a random UserID
        while (kill):
            rand = random.randint(0, 99999)
            cur.execute("select exists(select * from Users where UserID=?)", (rand, ))
            kill = cur.fetchone()[0] # returns a 1 if userID is taken, 0 otherwise
        cur.execute("insert into Users values(?, ?, ?, 0)", (rand, usern, passw))
        con.commit()
        return

    def help(self):
        if (self.help_code == 0): # 0 is not logged in
            print("Options: \n\tLogin\n\tCreate Account\n\tExit\n\tHelp")
        if ((self.help_code == 1) or self.help_code == 2):
            print("Options: \n\texit \n\tidk lmao")
        if (self.help_code == 2):
            print("Delete Account")

    def login(self):
        if (self.logged_in == 1):
            return
        # int = 0
        usern = input("INPUT USERNAME: ")
        passw = getpass.getpass("INPUT PASSWORD: ")
        cur.execute("select exists(select * from Users where Username=? AND Password=?)", (usern, passw))
        int = cur.fetchone()[0]
        if not (int):
            print("Wrong username or password")
            self.logged_in = int
            self.user = "Guest"
            return
        for row in cur.execute("select Admin, UserID from Users where Username=?", (usern, )):
            print("", end="") # do nothing command
        # user = User(usern, row[0], row[1])
        self.user.setName(usern)
        self.user.setAdmin(row[0])
        self.user.setID(row[1])
        self.logged_in = int
        self.help_code = 1
        # self.user = user
        return

    def authorSearch():
        author = input("INPUT AUTHOR NAME: ")
        for row in cur.execute("SELECT Title from Book where Author LIKE ?", (f"%{author}%", )):
            print(row[0])

# equivalent to a C main()
# starting the not definition code here

# adminFlag = 0
# logged_in = 0
# kill = 0
# user = 0
# list = [0, 0]
driver = Driver()
user_data = User()

while not(driver.logged_in):
    option = input("Guest % ").lower()
    if (option == "login"):
        driver.login()
    elif (option == "create account"):
        driver.create_account()
    elif (option == "exit"):
        if (input("Exit? (Y/n): ").lower() == "y"):
            exit()
    elif (option == "help"):
        driver.help()
    # try:
    #     func = getattr(Driver, "do_" + option)
    # except:
    #     print(f"Unknown command: '{option}', try 'help'")
    # else:
    #     list[0], list[1] = func()
    # if (list[0] != None):
    #     logged_in, user = list[0], list[1]

while(1):
    option = input(f"{driver.user.name} % ").lower()
    if (option == "help"):
        driver.help()
    elif (option == "exit"):
        if (input("Exit? (Y/n): ").lower() == "y"):
            exit()
    else:
        print(f"Unknown command: '{option}', try 'help'")

con.close()
# print("done")