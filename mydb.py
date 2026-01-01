from flask import flash
import sqlite3
#import pymysql
#import pymysql.cursors
from pymysql.converters import escape_string
'''
what do we need for external database commands?

get_a_route  - get a single route based on the route id
get_routes   - get a list of all routes
insert_route - insert a new route to the database
update_route - update an existing route
delete_route - delete a route based on route id
'''
class RouteDB:
    def __init__(self, config):

        self.config = {
                'host':'sirius.bobsplace.com',
                'user':'route',
                'password':'routes4cars',
                'database':'bobsplace'
        }
        self.db = None
        self.tuple_keys = ('id', 'title', 'date', 'owner', 'description',
                'route', 'footer', 'info', 'map_url', 'map', 'distance',
                'duration', 'rating', 'public')

    def OpenDB(self):
        db = sqlite3.connect('route_db.db')
        return db


    '''
    Get a single route given the route id
    '''
    def get_route(self, route):
        conn = self.OpenDB()
        cur = conn.cursor()
        cur.execute(f'SELECT id,title,date,owner,description,route,footer,info,map_url,map,distance,duration,rating,public from routes where id = {route}')
        result = cur.fetchall()
        cur.close()
        conn.close()

        # for sqlite3, this is an array with a single tuple
        # holding the record.  What we want to return is a
        # dict/json like structure

        inner_dict = dict(zip(self.tuple_keys, result[0]))

        return [inner_dict]

    '''
    Get a list of all the routes in the database. 

    Do we ever call this to get more than title/description?
    '''
    def get_routes(self):
        conn = self.OpenDB()
        cur = conn.cursor()
        cur.execute(f'SELECT id,title,date,owner,description,route,footer,info,map_url,map,distance,duration,rating,public from routes')
        result = cur.fetchall()
        cur.close()
        conn.close()

        ret = []
        for route in result:
            element = dict(zip(self.tuple_keys, route))
            ret.append(element)

        return ret

    '''
    Insert a new route into the database.
    '''
    def insert_route(self, fields):
        rating = 0
        public = 0
        route_id = 0

        conn = self.OpenDB()
        cur = conn.cursor()

        # fix up distance - needs to be float, not string
        if fields['distance'] == '':
            distance = 0.0
        else:
            distance = float(fields['distance'])

        try:
            query = 'INSERT into routes (title, date, owner, description, route, footer, info, map_url, distance, duration, rating, public) VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", {}, "{}", {}, {})'.format( fields['title'], fields['date'], fields['owner'], fields['description'].strip(), fields['route'].strip(), fields['footer'].strip(), fields['info'].strip(), fields['map_url'], distance, fields['duration'], rating, public)

            cur.execute(query)
            conn.commit()
            route_id = cur.lastrowid
        except pymysql.Error as er:
            print(er)
            flash(f'Route insert failed! {er}')
            cur.close()
            conn.close()
            return route_id

        cur.close()
        conn.close()
        return route_id        


    '''
    Update an existing route.
    '''
    def update_route(self, route_id, fields):
        conn = self.OpenDB()
        cur = conn.cursor()
        nf = {}
        print(f"FOOTER = {fields['footer']}")

        # Fix up fields by stripping white space
        for f in fields:
            nf[f] = escape_string(fields[f].strip())

        # fix up distance - needs to be float, not string
        if fields['distance'] == '':
            distance = 0.0
        else:
            distance = float(fields['distance'])

        print(f"MODIFIED FOOTER = {nf['footer']}")

        try:

            query = 'UPDATE routes SET title = "{}", owner = "{}", date = "{}", description = "{}", info = "{}", route = "{}", distance = {}, duration = "{}", map_url = "{}", footer = "{}" WHERE id = {}'.format(nf['title'], nf['owner'], nf['date'],
                    nf['description'], nf['info'], nf['route'],
                    distance, nf['duration'], nf['map_url'],
                    nf['footer'], int(route_id))

            print(f'{query}')
            cur.execute(query)
            conn.commit()

        # how do we trap errors for sqlite3?
        except:
            flash(f'Route update failed! (why?)')
            cur.close()
            conn.close()
            return False


    '''
    Given a route id, delete it from the database.
    '''
    def delete_route(self, route):
        conn = self.OpenDB()
        cur = conn.cursor()
        try:
            cur.execute(f'DELETE from routes where id = {route}')
            cur.close()
            conn.close()
        except pymysql.Error as er:
            print(er)
            cur.close()
            conn.close()

