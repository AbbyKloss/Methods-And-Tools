import sqlite3
import random # not necessarily a good idea in any actual implementation but it works for now
import bs4 as bs
import requests, sys

# because of webscraping, this takes a minute

hdr = {'User-Agent': 'Mozilla/5.0',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def getTable(url):
    source = requests.get(f'https://www.barnesandnoble.com{url}', headers=hdr).text

    soup = bs.BeautifulSoup(source,'html.parser')

    isbn, publisher, date, pages = "N/A", "N/A", "N/A", "N/A"

    for item in soup.find_all("table"):
        for tr in item.find_all("tr"):
            if ("ISBN" in tr.text):
                string = tr.text
                isbn = string[string.rfind(":")+3:-1]
            elif ("Publisher:" in tr.text):
                string = tr.text
                publisher = string[string.rfind(":")+3:-2]
            elif ("date" in tr.text):
                string = tr.text
                date = string[string.rfind(":")+2:-1]
            elif ("Pages" in tr.text):
                string = tr.text
                pages = string[string.rfind(":")+2:-1]
        return isbn, publisher, date, pages

con = sqlite3.connect("testdb.db")
cur = con.cursor()

print("Working...")

# Password text is a horrible idea, never do this in anything that matters
cur.execute(''' create table if not exists Users (
				UserID integer primary key,

                Username text,
                Password text,
                Payment text,
                Address text,
                Admin integer
				)''')

# uncomment any of these execute functions that you want, i just throw more in here when i need to add to the database and can't do that via the actual program
cur.execute(f"insert into Users values (00002, 'admin2', 'admin2', ?, ?, 1)", (None, None))
cur.execute(f"insert into Users values (00001, 'admin', 'admin', ?, ?, 1)", (None, None))
cur.execute(f"insert into Users values ({random.randint(0, 99999)}, '{'frankb75'}', 'password', '{random.randint(1000000000000000, 9999999999999999)}', '75 B. S. Hood Rd, Mississippi State, MS 39762', 0)")

# con.commit()

cur.execute(''' create table if not exists Book (
				ISBN integer primary key,

                Title text,
                Author text,
				Date text,
                Publisher text,
                Pages integer,
                Quantity integer,
                Cost real
				)''')

# all of these are bestsellers from barnes and noble
# scrapes as many as it can find
# this part takes a while
source = requests.get('https://www.barnesandnoble.com/b/books/_/N-1fZ29Z8q8?Nrpp=100', headers=hdr).text

soup = bs.BeautifulSoup(source,'html.parser')

books = len(soup.find_all("ol")[0].find_all("li"))
print(f"Books found: {books}")
booknum = 1

# print(len(str(booknum-1)))
# sys.stdout.flush()

for item in soup.find_all("ol"):
    for li in item.find_all("li"):
        print(f"\rScraping Book {booknum}/{books}", end="")
        base_string = li.find("div", {"class": "product-shelf-title"}).text
        title = base_string[1:base_string.rfind("(")-1]
        # date = base_string[base_string.rfind("("):-1]
        author = li.find("div", {"class": "product-shelf-author contributors"}).find("a").text
        price = li.find("span", {"class": "current"}).text[2:]
        for h3 in li.find_all("h3"):
            for a in h3.find_all("a"):
                isbn, publisher, date, pages = getTable(a["href"])
        cur.execute(f"insert into Book values (?, ?, ?, ?, ?, ?, {random.randint(1, 100)}, ?)", (isbn, title, author, date, publisher, pages, price))
        booknum += 1
print(" ")
# Cart is just a list of entries for a single user
cur.execute(''' create table if not exists Cart (
            UserID integer,
            ItemID,
            Quantity
            )''')


cur.execute(''' create table if not exists Orders (
            OrderID integer,
            ItemID integer,
            Quantity integer,
            UserID integer
            )''')
ran = random.randint(1000000000000, 9999999999999)
cur.execute(f"insert into Orders values (0, {ran}, 0, 0)")

print("Done")
con.commit()
con.close()
