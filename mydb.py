from flask import flash
import pymysql
import pymysql.cursors
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

    def OpenDB(self):
        db = pymysql.connect(
                host = self.config['host'],
                user = self.config['user'],
                password = self.config['password'],
                database = self.config['database']
                )
        return db


    '''
    Get a single route given the route id
    '''
    def get_route(self, route):
        conn = self.OpenDB()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(f'SELECT * from routes where id = {route}')
        result = cur.fetchall()
        cur.close()
        conn.close()

        return result

    '''
    Get a list of all the routes in the database. 

    Do we ever call this to get more than title/description?
    '''
    def get_routes(self):
        conn = self.OpenDB()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(f'SELECT * from routes')
        result = cur.fetchall()
        cur.close()
        conn.close()

        return result

    '''
    Insert a new route into the database.
    '''
    def insert_route(self, fields):
        rating = 0
        public = 0
        route_id = 0

        conn = self.OpenDB()
        cur = conn.cursor(pymysql.cursors.DictCursor)

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
        cur = conn.cursor(pymysql.cursors.DictCursor)
        nf = {}

        # Fix up fields by stripping white space
        for f in fields:
            nf[f] = escape_string(fields[f].strip())

        # fix up distance - needs to be float, not string
        if fields['distance'] == '':
            distance = 0.0
        else:
            distance = float(fields['distance'])


        try:

            query = 'UPDATE routes SET title = "{}", owner = "{}", date = "{}", description = "{}", info = "{}", route = "{}", distance = {}, duration = "{}", map_url = "{}", footer = "{}" WHERE id = {}'.format(nf['title'], nf['owner'], nf['date'],
                    nf['description'], nf['info'], nf['route'],
                    distance, nf['duration'], nf['map_url'],
                    nf['footer'], int(route_id))

            print(f'{query}')
            cur.execute(query)

        except pymysql.Error as er:
            print(er)
            flash(f'Route update failed! {er}')
            cur.close()
            conn.close()
            return False


    '''
    Given a route id, delete it from the database.
    '''
    def delete_route(self, route):
        conn = self.OpenDB()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cur.execute(f'DELETE from routes where id = {route}')
            cur.close()
            conn.close()
        except pymysql.Error as er:
            print(er)
            cur.close()
            conn.close()

