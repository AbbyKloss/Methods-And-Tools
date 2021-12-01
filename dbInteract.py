import sqlite3
import random
import getpass
# import os

# setting up sqlite3
con = sqlite3.connect("testdb.db")
cur = con.cursor()


# helper function, just centers a string and makes it a specified length
def centerString(string: str, length=15) -> str:
    output = ""
    if (len(string) <= length):
        long = length - (len(string))
        front = int(long/2)
        back = int((long/2) + (long % 2))
        output = (" " * front) + string + (" " * back)
    else:
        output = string[:length-3] + "..."
    return output

# getters and setters are lame, i can just access these bad boys
class User: 
    def __init__(self, usr="Guest", bool=False, id=0):
        self.name = usr
        self.admin = bool
        self.ID = id
    
    def updatePayment(self, ccn: int) -> None:
        cur.execute(f"update Users set Payment=? where UserID=?", (ccn, self.ID))

    def updateAddress(self, addr: str) -> None:
        cur.execute(f"update Users set Address=? where UserID=?", (addr, self.ID))

    def getPayment(self) -> int:
        cur.execute(f"select Payment from Users where UserID={self.ID}")
        ccn = cur.fetchone()[0]
        return ccn

    def getAddress(self) -> str:
        cur.execute(f"select Address from Users where UserID={self.ID}")
        addr = cur.fetchone()[0]
        return addr


class Cart:
    def __init__(self, user: User):
        self.user = user

    def checkExists(self, itemID: int) -> bool:
        cur.execute("select exists(select * from Cart where UserID=? and ItemID=?)", (self.user.ID, itemID))
        return cur.fetchone()[0]

    def removeItem(self, itemID: int) -> None:
        if self.checkExists(itemID):
            cur.execute("delete from Cart where UserID=? and ItemID=?", (self.user.ID, itemID))
        else:
            print("Item does not exist")
        con.commit()
    
    def changeQuantity(self, itemID: int, quantity: int) -> None:
        if self.checkExists(itemID):
            cur.execute("update Cart set Quantity=? where UserID=? and itemID=?", (quantity, self.user.ID, itemID))
        else:
            print("Item does not exist")
        con.commit()

    def addItem(self, itemID: int, quantity: int) -> None:
        # try:
        if not self.checkExists(itemID):
            cur.execute("insert into Cart values (?, ?, ?)", (self.user.ID, itemID, quantity))
        else:
            cur.execute("select Quantity from Cart where UserID=? and ItemID=?", (self.user.ID, itemID))
            quantity += cur.fetchone()[0]
            self.changeQuantity(itemID, quantity)
        # except:
        #     cur.execute("insert into Cart values (?, ?, ?)", (self.user.ID, itemID, quantity))
        con.commit()
    
    def clearCart(self) -> None:
        cur.execute(f"delete from Cart where UserID={self.user.ID}")
        con.commit()

    def viewCart(self) -> None:
        lenList = [30, 10]
        nameList = ["Title", "Quantity"]
        for i in range(len(nameList)):
            if (i != len(nameList)-1):
                print(centerString(nameList[i], lenList[i]), end="|")
            else:
                print(centerString(nameList[i], lenList[i]))
        cur.execute(f"select ItemID, Quantity from Cart where UserID=?", (self.user.ID, ))
        fetch = cur.fetchall()
        for row in fetch:
            for item in cur.execute(f"select Title from Book where ISBN={row[0]}"):
                title = item[0]
            itemList = [title, str(row[1])]
            for i in range(len(row)):
                if (i != len(row)-1):
                    print(centerString(itemList[i], lenList[i]), end="|")
                else:
                    print(centerString(itemList[i], lenList[i]))


class Driver: # dependent on classes User and Cart
    def __init__(self):
        self.user = User()
        self.cart = Cart(self.user)
        self.logged_in = 0
        self.help_code = 0

    # the most edited function, it goes here so i can find it easier
    def help(self):
        if (self.help_code == 0): # 0 is not logged in
            print("Options: \
                \n\tLogin\
                \n\tCreate Account\
                \n\tExit\
                \n\tHelp\
                ")
        if ((self.help_code == 1) or self.help_code == 2): # 1 is logged in
            print("Options:\
                \n\tLogout\
                \n\tExit\
                \n\tSearch [-t, -a, -p, -d]\
                \n\tAdd to Cart\
                \n\tRemove from Cart\
                \n\tChange Quantity of Item in Cart\
                \n\tClear Cart\
                \n\tView Cart\
                \n\tCheckout\
                \n\tUpdate Payment\
                \n\tUpdate Address\
                ")
        if (self.help_code == 2): # 2 is admin
            print("\tDelete Account")

    # possibly prone to sql injection
    # tried to do injection, it didn't work. there's a chance idk how to do it
    # returns -1 on failure, 0 on success
    def create_account(self):
        if (self.logged_in == 1):
            print(f"Unknown command: 'create account', try 'help'")
            return
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
        cur.execute("insert into Users values(?, ?, ?, NULL, NULL, 0)", (rand, usern, passw))
        con.commit()
        return

    def login(self):
        i = 0
        # if logged in, pretend this doesn't exist
        if (self.logged_in == 1):
            print(f"Unknown command: 'login', try 'help'")
            return
        # get user credentials
        # 3 attempts before kicking out
        while(1):
            usern = input("INPUT USERNAME: ")
            passw = getpass.getpass("INPUT PASSWORD: ")
            # make sure they're correct
            cur.execute("select exists(select * from Users where Username=? AND Password=?)", (usern, passw))
            int = cur.fetchone()[0]
            i += 1
            if ((not int) and (i < 3)):
                print("Wrong username or password")
            elif (i == 3):
                print("3 incorrect login attempts")
                return
            else:
                break
        # update necessary info
        for row in cur.execute("select Admin, UserID from Users where Username=?", (usern, )):
            print("", end="") # do nothing command
        self.user.name = usern
        self.user.admin = row[0]
        self.user.ID = row[1]
        # self.cart.user.ID = self.user.ID # don't think this is necessary
        self.logged_in = int
        
        if (self.user.admin):
            self.help_code = 2
        else:
            self.help_code = 1
        return

    def handleSearch(self, input):
        inputList = input.split()
        try:
            if ((inputList[1] == "-a") or (inputList[1] == "author")):
                self.bookSearch("Author")
            elif ((inputList[1] == "-d") or (inputList[1] == "date")):
                self.bookSearch("Date")
            elif ((inputList[1] == "-p") or (inputList[1] == "publisher")):
                self.bookSearch("Publisher")
            else:
                self.bookSearch("Title")
        # if no search flags are input
        except IndexError:
            self.bookSearch("Title")

    def bookSearch(self, option):
        # make sure the user is logged in at all, no guests allowed
        if (self.logged_in == 0):
            print(f"Unknown command: '{option.lower()}Search', try 'help'")
            return
        # get user input
        query = input(f"INPUT {option.upper()}: ")
        # make sure it exists
        cur.execute(f"select exists(SELECT * from Book where {option} LIKE ?)", (f"%{query}%", ))
        if not (cur.fetchone()[0]):
            print(f"No {option.lower()} found by that name")
            return
        # finding and representing the data
        lengthList = [14, 30, 20, 12, 20, 7, 10, 8]
        labelList = ["ISBN", "Title", "Author", "Date", "Publisher", "Pages", "Quantity", "Cost"]
        for i in range(len(lengthList)):
            print(centerString(labelList[i], lengthList[i]), end="")
            if (i != len(lengthList)-1):
                print("|", end="")
            else:
                print("")
        for row in cur.execute(f"SELECT * from Book where {option} LIKE ?", (f"%{query}%", )):
            for i in range(len(row)):
                print(centerString(str(row[i]), lengthList[i]), end="")
                if (i != len(row)-1):
                    print("|", end="")
                else:
                    print("")

    def delete_account(self):
        # if the user isn't an admin, pretend it doesn't exist
        if not (self.user.admin):
            print(f"Unknown command: 'delete account', try 'help'")
            return
        # make sure they are who they say they are
        password = getpass.getpass(f"Password for {self.user.name}: ")
        cur.execute("select exists(select * from Users where Username=? AND Password=?)", (self.user.name, password))
        if not (cur.fetchone()[0]):
            print("Incorrect Password")
            return
        # get user input
        password = input("Enter username to delete: ") # reusing variables
        if (self.user.name == password):
            print("Cannot delete self")
            return
        # check to make sure the user exists
        cur.execute("select exists(select * from Users where Username=?)", (password, ))
        if not (cur.fetchone()[0]):
            print(f"User '{password}' does not exist")
            return
        # make sure the user isn't an admin
        cur.execute("select exists(select * from Users where Username=? AND Admin=?)", (password, 0))
        if not (cur.fetchone()[0]):
            print("Permission Denied")
            return
        # delete
        cur.execute("delete from Users where Username=?", (password, ))
        con.commit()

    def logout(self):
        # set everything to defaults
        self.logged_in = 0
        self.help_code = 0
        self.user.name = "Guest"
        self.user.admin = False
        self.user.ID = 0
        # self.cart.userID = 0
        return

    def updatePayment(self):
        ccn = int(input("Enter Credit Card Number: "))
        self.user.updatePayment(ccn)
    
    def updateAddress(self):
        addr = input("Enter Address: ")
        self.user.updateAddress(addr)

    def checkInfo(self):
        print("Payment: ", self.user.getPayment())
        print("Address: ", self.user.getAddress())

    def checkout(self):
        cur.execute("select max(OrderID) from Orders")
        orderID = cur.fetchone()[0]+1
        cartList = []
        cur.execute("select ItemID, Quantity from Cart where UserID=?", (self.user.ID, ))
        fetch = cur.fetchall()
        sum = 0
        for row in fetch:
            quantity = row[1]
            isbn = row[0]
            # cur.execute("insert into Orders values(?, ?, ?, ?)", (orderID, row[0], row[1], self.user.ID))
            cur.execute("select Quantity, Title, Cost from Book where ISBN=?", (isbn,))
            fet = cur.fetchall()
            for item in fet:
                instock = item[0]
                if (instock < quantity):
                    print(f"We do not have enough stock left of {centerString(item[1], 15)} for this transaction.")
                    response = input("Would you like the remainder? (y/n): ").lower()
                    if response.startswith("y"):
                        quantity = instock
                    else:
                        print("Removing item...")
                        quantity = 0
                if (quantity):
                    sum += quantity * item[2]
                    cartList.append([orderID, isbn, quantity, self.user.ID, instock])
        print(f"Total cost is: {sum}")
        response = input("Is this ok? (y/n): ").lower()
        if response.startswith("y"):
            cur.execute("select Payment, Address from Users where UserID=?", (self.user.ID, ))
            payment, address = cur.fetchone()
            if (payment == None) or (address == None):
                print("Payment and/or Address needs to be updated")
                response = input("Update now? (Y/n): ").lower()
                if response.startswith("y"):
                    if (address == None):
                        self.updateAddress()
                    if (payment == None):
                        self.updatePayment()
                    
                else:
                    return
            for item in cartList:
                cur.execute("insert into Orders values(?, ?, ?, ?)", (item[0], item[1], item[2], item[3]))
                cur.execute(f"update Book set Quantity={item[4]-item[2]} where ISBN={item[1]}")
            self.cart.clearCart()
            con.commit()
                
        



# exit handler
def atexit():
    con.close()
    exit()

# menu for when logged out
def logged_out():
    while not(driver.logged_in):
        # obtaining user input
        option = input("Guest % ").lower()
        # try:
        #     flags = option.split()[1:]
        # except:
        #     flags = ""

        # processing user input
        if (option == "login"):
            driver.login()

        elif (option == "create account"):
    
            driver.create_account()

        elif (option == "exit"):
            if (input("Exit? (Y/n): ").lower() == "y"):
                atexit()

        elif (option == "help"):
            driver.help()

        else:
            print(f"Unknown command: '{option}', try 'help'")
        # try:
        #     controller = getattr(Driver, option)
        # except AttributeError:
        #     print(f"Unknown command: '{option}', try 'help'")
        # else:
        #     controller(driver, flags)

    # triggers when the while loop ends
    return logged_in()

# menu for when logged in
def logged_in():
    while(1):
        # getting user input
        option = input(f"{driver.user.name} % ").lower()
        # try:
        #     flags = option.split()[1:]
        # except:
        #     flags = ""

        # processing user input
        if (option == ""):
            print("", end="")

        elif (option == "help"):
            driver.help()

        elif (option == "exit"):
            if (input("Exit? (Y/n): ").lower() == "y"):
                atexit()

        elif (option == "delete account"):
            driver.delete_account()

        elif (option.split()[0] == "search"):
            driver.handleSearch(option)

        elif (option == "logout"):
            return driver.logout()

        elif option.startswith("add"):
            isbn = int(input("Enter the item's ISBN: "))
            quantity = int(input("Enter the number of items: "))
            return driver.cart.addItem(isbn, quantity)
        
        elif option.startswith("remove"):
            isbn = int(input("Enter the item's ISBN: "))
            return driver.cart.removeItem(isbn)

        elif option.startswith("change"):
            isbn = int(input("Enter the item's ISBN: "))
            quantity = int(input("Enter the total number of this item desired: "))
            return driver.cart.changeQuantity(isbn, quantity)

        elif option.startswith("clear"):
            verify = input("Clear the cart? (y/n): ").lower()
            if (verify.startswith("y")):
                driver.cart.clearCart()
            else:
                print("Action cancelled")

        elif option.startswith("view"):
            driver.cart.viewCart()

        elif option.startswith("checkout"):
            driver.checkout()

        elif option == "check":
            driver.checkInfo()

        elif option.startswith("update"):
            if (option[7:].startswith("p")):
                driver.updatePayment()
            elif (option[7:].startswith("a")):
                driver.updateAddress()
            else:
                print(f"Unknown command: '{option}', try 'help'")

        else:
            print(f"Unknown command: '{option}', try 'help'")
        # try:
        #     controller = getattr(Driver, option)
        # except AttributeError:
        #     print(f"Unknown command: '{option}', try 'help'")
        # else:
        #     controller(driver, flags)


# equivalent to a C main()
# starting the not class/function definition code here
driver = Driver()

# at most, you'll be 3 functions deep at any given moment
while(1):
    logged_out()