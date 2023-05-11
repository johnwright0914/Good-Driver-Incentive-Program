import mysql.connector

# 
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Reddog1298@",
    database = "mydatabase"
)

mycursor = mydb.cursor()
# create table
# mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")
# create table with primary key
# mycursor.execute("CREATE TABLE customers1 (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255))")
# add primary key to exsisting table
#mycursor.execute("ALTER TABLE customers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")

# show all tables
#mycursor.execute("SHOW TABLES")

"""
# add a  single record to a table
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val_single = ("John", "Highway 21")
val_mult = [
    ('Peter', "Lowstreet 4"),
    ('Amy', 'Apple st 63'),
    ('Micheal', 'Ocean Ave 234')
]
val3 = ('Michelle', 'Blue Lane 3')

# execute single record
mycursor.execute(sql, val3)
# execute multiple records
#mycursor.executemany(sql, val_mult)

# this is required to commit changes to the database
mydb.commit()
#print(mycursor.rowcount, "record inserted.")
print("1 record inserted, ID:", mycursor.lastrowid)
"""
"""
# select records from a database
mycursor.execute("SELECT * FROM customers")

# select only some coloumns
#mycursor.execute("SELECT name, address FROM customers")
#result = mycursor.fetchall()

# fetch a single item from database
result = mycursor.fetchone()
"""

"""
# select records that match
sql = "SELECT * FROM customers WHERE address ='Highway 21'"
mycursor.execute(sql)
result = mycursor.fetchall()
"""

"""
# use of wildcards
#sql = "SELECT * FROM customers WHERE address LIKE '%2%'" # all address with a 2 in them
# use of escapes to prevent SQL injections
sql = "SELECT * FROM customers WHERE address = %s"
adr = ("Ocean Ave 234", )
mycursor.execute(sql, adr)
result = mycursor.fetchall()
"""
"""
# sort results of query
#sql  = "SELECT * FROM customers ORDER BY name"
# sort descending
sql = "SELECT * FROM customers ORDER BY name DESC"

mycursor.execute(sql)
result = mycursor.fetchall()

for x in result:
    print(x)
"""
"""
# delete a record from the database
sql = "DELETE FROM customers WHERE address = %s"
adr = ('Ocean Ave 234', )

mycursor.execute(sql, adr)
mydb.commit()

print (mycursor.rowcount, "reocrd(s) deleted")
"""

"""
# delete a table
#sql = "DROP TABLE customers1"
# delete only if it exsists
sql = "DROP TABLE IF EXSISTS customers1"
mycursor.execute(sql)
"""
"""
# update records in database
sql = "UPDATE customers SET address = %s WHERE address = %s"
val = ("Banna Rd 36", "Apple st 63")
mycursor.execute(sql, val)
mydb.commit()
print(mycursor.rowcount, "records(s) affected")
"""
"""
# limit results of a query
#mycursor.execute("SELECT * FROM customers LIMIT 4")
# limit and start from an offset
mycursor.execute("SELECT * FROM customers LIMIT 5 OFFSET 2")
results = mycursor.fetchall()

for x in results:
    print(x)
"""

# examples of joining two tables
# tables contain users with fav value that links to ids in products table
sql = "SELECT \
    users.name AS user, \
    products.name AS favorite \
    FROM users \
    INNER JOIN products ON users.fav = products.id"

mycursor.execute(sql)

for x in mycursor:
    print(x)
