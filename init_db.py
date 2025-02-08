import sqlite3
import mysql.connector

oldroutes = mysql.connector.connect(
        host='sirius.bobsplace.com',
        user='route',
        password='routes4cars',
        database='bobsplace'
        )

cursor = oldroutes.cursor()
cursor.execute("SELECT * from routes")
result = cursor.fetchall()

'''
results:
    0 id
    1 title
    2 date
    3 owner
    4 description
    5 route
    6 footer
    7 info
    8 map_url
    9 map
    10 distance
    11 duration
    12 rating
    13 rate
    14 public
'''
#print(f'{result[0][1]} {result[0][14]}')
for x in result:
    l = list(x)
    print(type(l))
    print(f'{l[1]} {l[2]} {l[10]} {l[9]}')

connection = sqlite3.connect('route_db.db')

with open('schema.sql') as f:
    connection.executescript(f.read())


cur = connection.cursor()

#insert records here
for x in result:
    l = list(x)
    for d in range(0, len(l)):
        if d == 10 and l[d] == None:
            l[d] = 0.0
        if d == 9 and l[d] == None:
            l[d] = b''
        if d == 12 and l[d] == None:
            l[d] = 0
        if d == 14 and l[d] == None:
            l[d] = 0
        if l[d] == None:
            l[d] = ''
        print(f'type of {d} = {type(l[d])}')

    cur.execute("INSERT into routes(title, date, owner, description, route, footer, info, map_url, map, distance, duration, rating, public) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9], float(l[10]), l[11], l[12], l[14])
            )

'''
cur.execute("INSERT into routes(title...) VALUES (?...)",
        (data, data, data)
        )
'''

connection.commit()
connection.close()
