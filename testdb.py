import sqlite3
import random # not necessarily a good idea in any actual implementation but it works for now

con = sqlite3.connect("testdb.db")
cur = con.cursor()

# Password text is a horrible idea, never do this in anything that matters
cur.execute(''' create table if not exists Users (
				UserID integer primary key,

                Username text,
                Password text,
                Admin integer
				)''')

# uncomment any of these execute functions that you want, i just throw more in here when i need to add to the database and can't do that via the actual program
# cur.execute(f"insert into Users values (00002, 'admin2', 'admin2', 1)")
# cur.execute(f"insert into Users values (00001, 'admin', 'admin', 1)")
# cur.execute(f"insert into Users values ({random.randint(0, 99999)}, 'georgef88', 'password', 0)")

cur.execute(''' create table if not exists Book (
				ISBN integer primary key,

                Title text,
                Author text,
				Date text,
                Publisher text,
                Pages integer,
                Quantity integer
				)''')

# all of these are bestsellers from barnes and noble
# https://www.barnesandnoble.com/b/books/_/N-1fZ29Z8q8
# cur.execute(f"insert into Book values (9780441013593, 'Dune', 'Frank Herbert', '08/02/2005', 'Penguin Publishing Group', 704, {random.randint(1, 100)})")
# cur.execute(f"insert into Book values (9781974709939, 'Chainsaw Man Vol. 1', 'Tatsuki Fujimoto', '10/26/2020', 'Viz Media LLC', 192, {random.randint(1, 100)})")
# cur.execute(f"insert into Book values (9781984877925, 'Will', 'Will Smith', '11/09/2021', 'Penguin Publishing Group', 432, {random.randint(1, 100)})")

con.commit()
con.close()
