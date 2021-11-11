import sqlite3

con = sqlite3.connect("testdb.db")
cur = con.cursor()

cur.execute(''' create table if not exists Book (
				ISBN integer primary key,

                Title text,
                Author text,
				Date text,
                Publisher text,
                Pages integer
				)''')

# all of these are bestsellers from barnes and noble
# https://www.barnesandnoble.com/b/books/_/N-1fZ29Z8q8

cur.execute("insert into Book values (9780441013593, 'Dune', 'Frank Herbert', '08/02/2005', 'Penguin Publishing Group', 704)")
cur.execute("insert into Book values (9781974709939, 'Chainsaw Man Vol. 1', 'Tatsuki Fujimoto', '10/26/2020', 'Viz Media LLC', 192)")
cur.execute("insert into Book values (9781984877925, 'Will', 'Will Smith', '11/09/2021', 'Penguin Publishing Group', 432)")

con.commit()
con.close()
