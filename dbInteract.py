import sqlite3
import random
import getpass
# import os

# setting up sqlite3
connected_database = sqlite3.connect("testdb.db")
cursor = connected_database.cursor()


# helper function, just centers a string and makes it a specified length
def centerString(string: str, length: int=15) -> str:
    '''Centers a string within a space defined in length'''
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
    def __init__(self, usr="Guest", bool=False, id: int=0):
        self.name = usr
        self.admin = bool
        self.ID = id
    
    def updatePayment(self, ccn: int) -> None:
        '''Sets user's credit card number in database'''
        cursor.execute(f"update Users set Payment=? where UserID=?", (ccn, self.ID))

    def updateAddress(self, addr: str) -> None:
        '''Sets user's address in database'''
        cursor.execute(f"update Users set Address=? where UserID=?", (addr, self.ID))

    def getPayment(self) -> int:
        '''Retrieves user's credit card number from database'''
        cursor.execute(f"select Payment from Users where UserID={self.ID}")
        credit_card_number = cursor.fetchone()[0]
        return credit_card_number

    def getAddress(self) -> str:
        '''Retrieves user's address from database'''
        cursor.execute(f"select Address from Users where UserID={self.ID}")
        addr = cursor.fetchone()[0]
        return addr


class Cart:
    def __init__(self, user: User):
        self.user = user

    def checkExists(self, itemID: int) -> bool:
        cursor.execute("select exists(select * from Cart where UserID=? and ItemID=?)", (self.user.ID, itemID))
        return cursor.fetchone()[0]

    def removeItem(self, itemID: int) -> None:
        if self.checkExists(itemID):
            cursor.execute("delete from Cart where UserID=? and ItemID=?", (self.user.ID, itemID))
        else:
            print("Item does not exist")
        connected_database.commit()
    
    def changeQuantity(self, itemID: int, quantity: int) -> None:
        if self.checkExists(itemID):
            cursor.execute("update Cart set Quantity=? where UserID=? and itemID=?", (quantity, self.user.ID, itemID))
        else:
            print("Item does not exist")
        connected_database.commit()

    def addItem(self, itemID: int, quantity: int) -> None:
        # try:
        if not self.checkExists(itemID):
            cursor.execute("insert into Cart values (?, ?, ?)", (self.user.ID, itemID, quantity))
        else:
            cursor.execute("select Quantity from Cart where UserID=? and ItemID=?", (self.user.ID, itemID))
            quantity += cursor.fetchone()[0]
            self.changeQuantity(itemID, quantity)
        # except:
        #     cur.execute("insert into Cart values (?, ?, ?)", (self.user.ID, itemID, quantity))
        connected_database.commit()
    
    def clearCart(self) -> None:
        cursor.execute(f"delete from Cart where UserID={self.user.ID}")
        connected_database.commit()

    def viewCart(self) -> None:
        lenList = [30, 10]
        nameList = ["Title", "Quantity"]
        for i in range(len(nameList)):
            if (i != len(nameList)-1):
                print(centerString(nameList[i], lenList[i]), end="|")
            else:
                print(centerString(nameList[i], lenList[i]))
        cursor.execute(f"select ItemID, Quantity from Cart where UserID=?", (self.user.ID, ))
        fetch = cursor.fetchall()
        for row in fetch:
            for item in cursor.execute(f"select Title from Book where ISBN={row[0]}"):
                title = item[0]
            itemList = [title, str(row[1])]
            for i in range(len(row)):
                if (i != len(row)-1):
                    print(centerString(itemList[i], lenList[i]), end="|")
                else:
                    print(centerString(itemList[i], lenList[i]))

    def viewOrders(self) -> None:
        lenList = [30, 10]
        nameList = ["Title", "Quantity"]
        for i in range(len(nameList)):
            if (i != len(nameList)-1):
                print(centerString(nameList[i], lenList[i]), end="|")
            else:
                print(centerString(nameList[i], lenList[i]))
        cursor.execute(f"select ItemID, Quantity from Orders where UserID=?", (self.user.ID, ))
        fetch = cursor.fetchall()
        for row in fetch:
            for item in cursor.execute(f"select Title from Book where ISBN={row[0]}"):
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
        '''Tells the user what they can do at any given time'''
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
                \n\tOrder History\
                \n\tUpdate Payment\
                \n\tUpdate Address\
                \n\tCheck Info\
                ")
        if (self.help_code == 2): # 2 is admin
            print("\tDelete Account")

    # possibly prone to sql injection
    # tried to do injection, it didn't work. there's a chance idk how to do it
    # returns -1 on failure, 0 on success
    def create_account(self) -> None:
        '''Creates an account from the login screen'''
        if (self.logged_in == 1):
            print(f"Unknown command: 'create account', try 'help'")
            return
        usern = input("Input Username:  ")
        passw = getpass.getpass("Input Password:  ")
        # pass2 = input("VERIFY PASSWORD: ")
        if (passw != getpass.getpass("Verify Password: ")):
            print("Passwords don't match")
            return
        cursor.execute("select exists(select * from Users where Username=?)", (usern, ))
        if (int(cursor.fetchone()[0])):
            print("Username already taken")
            return
        kill = 1
        # finds a random UserID
        while (kill):
            rand = random.randint(0, 99999)
            cursor.execute("select exists(select * from Users where UserID=?)", (rand, ))
            kill = cursor.fetchone()[0] # returns a 1 if userID is taken, 0 otherwise
        cursor.execute("insert into Users values(?, ?, ?, NULL, NULL, 0)", (rand, usern, passw))
        connected_database.commit()
        return

    def login(self) -> None:
        '''Guides the user through the logging in process'''
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
            cursor.execute("select exists(select * from Users where Username=? AND Password=?)", (usern, passw))
            int = cursor.fetchone()[0]
            i += 1
            if ((not int) and (i < 3)):
                print("Wrong username or password")
            elif (i == 3):
                print("3 incorrect login attempts")
                return
            else:
                break
        # update necessary info
        for row in cursor.execute("select Admin, UserID from Users where Username=?", (usern, )):
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

    def handleSearch(self, input: str) -> None:
        '''helper function for searching'''
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

    def bookSearch(self, option: str) -> None:
        # make sure the user is logged in at all, no guests allowed
        if (self.logged_in == 0):
            print(f"Unknown command: '{option.lower()}Search', try 'help'")
            return
        # get user input
        query = input(f"INPUT {option.upper()}: ")
        # make sure it exists
        cursor.execute(f"select exists(SELECT * from Book where {option} LIKE ?)", (f"%{query}%", ))
        if not (cursor.fetchone()[0]):
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
        for row in cursor.execute(f"SELECT * from Book where {option} LIKE ?", (f"%{query}%", )):
            for i in range(len(row)):
                print(centerString(str(row[i]), lengthList[i]), end="")
                if (i != len(row)-1):
                    print("|", end="")
                else:
                    print("")

    def delete_account(self) -> None:
        '''Guides admins through deleting accounts'''
        # if the user isn't an admin, pretend it doesn't exist
        if not (self.user.admin):
            print(f"Unknown command: 'delete account', try 'help'")
            return
        # make sure they are who they say they are
        password = getpass.getpass(f"Password for {self.user.name}: ")
        cursor.execute("select exists(select * from Users where Username=? AND Password=?)", (self.user.name, password))
        if not (cursor.fetchone()[0]):
            print("Incorrect Password")
            return
        # get user input
        password = input("Enter username to delete: ") # reusing variables
        if (self.user.name == password):
            print("Cannot delete self")
            return
        # check to make sure the user exists
        cursor.execute("select exists(select * from Users where Username=?)", (password, ))
        if not (cursor.fetchone()[0]):
            print(f"User '{password}' does not exist")
            return
        # make sure the user isn't an admin
        cursor.execute("select exists(select * from Users where Username=? AND Admin=?)", (password, 0))
        if not (cursor.fetchone()[0]):
            print("Permission Denied")
            return
        # delete
        cursor.execute("delete from Users where Username=?", (password, ))
        connected_database.commit()

    def logout(self) -> None:
        if (self.logged_in == 0):
            print(f"Unknown command: 'logout', try 'help'")
            return
        # set everything to defaults
        self.logged_in = 0
        self.help_code = 0
        self.user.name = "Guest"
        self.user.admin = False
        self.user.ID = 0
        # self.cart.userID = 0
        return

    def updatePayment(self) -> None:
        if (self.logged_in == 0):
            print(f"Unknown command: 'update payment', try 'help'")
            return
        ccn = int(input("Enter Credit Card Number: "))
        self.user.updatePayment(ccn)
    
    def updateAddress(self) -> None:
        if (self.logged_in == 0):
            print(f"Unknown command: 'update address', try 'help'")
            return
        addr = input("Enter Address: ")
        self.user.updateAddress(addr)

    def checkInfo(self) -> None:
        if (self.logged_in == 0):
            print(f"Unknown command: 'Check Info', try 'help'")
            return
        print("Payment: ", self.user.getPayment())
        print("Address: ", self.user.getAddress())

    def checkout(self) -> None:
        if (self.logged_in == 0):
            print(f"Unknown command: 'Checkout', try 'help'")
            return
        cursor.execute("select max(OrderID) from Orders")
        orderID = cursor.fetchone()[0]+1
        cartList = []
        cursor.execute("select ItemID, Quantity from Cart where UserID=?", (self.user.ID, ))
        fetch = cursor.fetchall()
        sum = 0
        for row in fetch:
            quantity = row[1]
            isbn = row[0]
            # cur.execute("insert into Orders values(?, ?, ?, ?)", (orderID, row[0], row[1], self.user.ID))
            cursor.execute("select Quantity, Title, Cost from Book where ISBN=?", (isbn,))
            fet = cursor.fetchall()
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
            cursor.execute("select Payment, Address from Users where UserID=?", (self.user.ID, ))
            payment, address = cursor.fetchone()
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
                cursor.execute("insert into Orders values(?, ?, ?, ?)", (item[0], item[1], item[2], item[3]))
                cursor.execute(f"update Book set Quantity={item[4]-item[2]} where ISBN={item[1]}")
            self.cart.clearCart()
            connected_database.commit()
                

# exit handler
def atexit() -> None:
    '''Exit Handler'''
    connected_database.close()
    exit()

# menu for when logged out
def logged_out() -> None:
    '''Handles the act of being logged out from the site'''
    while not(driver.logged_in):
        # obtaining user input
        option = input("Guest % ").lower()

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

    # triggers when the while loop ends
    return logged_in()

# menu for when logged in
def logged_in() -> None:
    '''Handles the act of being logged in to the site'''
    while(1):
        # getting user input
        option = input(f"{driver.user.name} % ").lower()

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

        elif option.startswith("order"):
            driver.cart.viewOrders()

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

# equivalent to a C main()
# starting the not class/function definition code here
driver = Driver()

# at most, you'll be 3 functions deep at any given moment
while(1):
    logged_out()