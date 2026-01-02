'''
Convert the route data in the mariadb database and insert it
into a sqlite3 database.
'''

import sqlite3
import pymysql
import pymysql.cursors
from pymysql.converters import escape_string

#import mysql.connector

oldroutes = pymysql.connect(
                host = 'sirius.bobsplace.com',
                user = 'route',
                password = 'routes4cars',
                database = 'bobsplace'
                )


cursor = oldroutes.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT * from routes")
result = cursor.fetchall()
cursor.close()
oldroutes.close()


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
#print(f'{result[0][1]} {result[0][10]} {result[0][11]} {result[0][14]}')
for x in result:
    # x is a dictionary {'id':1, 'title':'a title'...}
    # if we convert it to a list we get a list of field names
    #  ['id', 'title', 'date', 'owner', 'description', 'route', 'footer', 'info', 'map_url', 'map', 'this', 'what', 'distance', 'duration', 'rating', 'public']
    # so I think we want to use:
    #  x['id'] to get the value
    #l = list(x)
    #print('list = {}'.format(l))
    #print(f'TEST ... {l[1]} {l[2]} {l[10]} {l[11]}')

    print('X = {} - {}'.format(x['id'], x['title']))
    '''
    for key in x:
        print(f'key = {key}')
    '''

connection = sqlite3.connect('route_db.db')

try:
    with open('schema.sql') as f:
        connection.executescript(f.read())
except:
    print(f'Table routes already exists')

cur = connection.cursor()

#insert records here
for x in result:
    # convert None values to 0 or ''
    for key in x:
        if x[key] == None:
            if key == 'title': x[key] = ''
            if key == 'date': x[key] = ''
            if key == 'owner': x[key] = ''
            if key == 'description': x[key] = ''
            if key == 'route': x[key] = ''
            if key == 'footer': x[key] = ''
            if key == 'info': x[key] = ''
            if key == 'map_url': x[key] = ''
            if key == 'map': x[key] = ''
            #if key == 'what': x[key] = 0
            if key == 'distance': x[key] = 0.0
            if key == 'duration': x[key] = ''
            if key == 'rating': x[key] = 0
            if key == 'public': x[key] = 0
        # strip leading/trailing white space from titles
        if key == 'title':
            x[key] = x[key].strip()
        if key == 'description':
            x[key] = x[key].replace('eâ€™', '\'')
            x[key] = x[key].replace('Ã¢â‚¬â„¢', '\'')
            # x[key] = escape_string(x[key]) not needed?
        if key == 'date':
            x[key] = x[key].strftime('%Y-%m-%d')

    sql_query = "INSERT INTO routes(title, date, owner, description, route, footer, info, map_url, map, distance, duration, rating, public) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cur.execute(sql_query,
            (x['title'], x['date'], x['owner'], x['description'],
             x['route'], x['footer'], x['info'], x['map_url'], x['map'],
             float(x['distance']), x['duration'], x['rating'], x['public'])
            )

connection.commit()
connection.close()
