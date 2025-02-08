import sqlite3
from flask import Flask
from flask import render_template
from flask import request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = '3asdfki5489907asLJO8dka378'

@app.context_processor
def inject_verions():
    return dict(version="Version 3.0.0", date="02/08/2025")
@app.context_processor
def inject_format():
    # default, PCA, RM
    return dict(format="default")


log = open('log.txt', 'w')
last_id = 0

def log_it(it):
    log.write(f'{it}\n')
    log.flush()

def get_db_connection():
    conn = sqlite3.connect('route_db.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_route(route_id):
    conn = get_db_connection()
    routes = conn.execute(f'SELECT * from routes where id = {route_id}').fetchall()
    conn.close()
    return routes

def db_insert(form):
    title = form['title']
    owner = form['owner']
    date = form['date']
    description = form['description']
    info = form['info']
    route = form['route']
    distance = form['distance']
    duration = form['duration']
    map_url = form['map_url']
    footer = form['footer']
    rating = ''
    public = 0

    # add other fields to check
    if not title: 
        flash('Title is required!')
        return False
    else:
        # Insert into database
        flash(f'insert {title} into database')
        if form['action'] == 'Submit':
            # insert database record
            conn = get_db_connection()
            try:
                conn.execute("INSERT into routes "
                    "(title, date, owner, description, route, footer, info, map_url, distance, duration, rating, public) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (title, date, owner, description, route, footer, info, map_url, distance, duration, rating, public)
                )
                conn.commit()
            except sqlite3.Error as er:
                print(er.sqlite_errorcode)
                print(er.sqlite_errorname)
                flash(f'Route update failed! {er.sqlite_errorname}')
                conn.close()
                return False

            conn.close()
    return True

class ROUTE:
    def __init__(self, raw):
        self.raw = raw

    '''
    Process a route instruction line
    '''
    def line_processor(self, line, line_no, flag):
        td_l = '<tr><td style="padding-right: 10px" align="right">{}</td>'
        td_n = '<td style="padding-right: 10px" align="right">{}</td>'
        td_i = '<td style="padding-left: 10px" align="left">{}</td>'
        td_x = '<td style="padding-left: 10px" align="left">{}</td></tr>\n'

        # a line is supposed to look like <code|mileage>|<text>
        # where code is '-' for note, and 'rm' for rallymaster note
        parts = line.split('|')
        num = line_no + 1

        if len(parts) > 1:
            miles = parts[0]
            text = parts[1]
            text = text.replace('LEFT','<b>LEFT</b>')
            text = text.replace('RIGHT','<b>RIGHT</b>')
            text = text.replace('STRAIGHT','<b>STRAIGHT</b>')
            text = text.replace('SIGNAL','<b>SIGNAL</b>')
            text = text.replace('STOP','<b>STOP</b>')
            text = text.replace('T ','<b>T </b>')
            text = text.replace('Y ','<b>Y </b>')
            text = text.replace('Y.','<b>Y.</b>')
            text = text.replace('Y,','<b>Y,</b>')
            text = text.replace('CAST','<b>CAST</b>')
            if len(parts) > 2:
                extra = parts[2]
            else:
                extra = ''
            if miles == '-':
                new_line = td_l.format('&nbsp;') + td_n.format('&nbsp;') + td_i.format(text) + td_x.format(extra)
            elif miles == 'rm' and flag:
                new_line = td_l.format('') + td_n.format('') + td_i.format(text) + td_x.format(extra)
            else: # must be a mileage
                new_line = td_l.format(num) + td_n.format(miles) + td_i.format(text) + td_x.format(extra)
        else:  # Instruction, but no milage
            miles = ''
            text = parts[0]
            text = text.replace('LEFT','<b>LEFT</b>')
            text = text.replace('RIGHT','<b>RIGHT</b>')
            text = text.replace('STRAIGHT','<b>STRAIGHT</b>')
            text = text.replace('SIGNAL','<b>SIGNAL</b>')
            text = text.replace('STOP','<b>STOP</b>')
            text = text.replace('T ','<b>T </b>')
            text = text.replace('Y ','<b>Y </b>')
            text = text.replace('Y.','<b>Y.</b>')
            text = text.replace('Y,','<b>Y,</b>')
            text = text.replace('CAST','<b>CAST</b>')
            new_line = td_l.format(num) + td_n.format(miles) + td_i.format(text) + td_x.format('')

        return new_line


    def toHTML(self):
        lines = self.raw.split('\n')

        html = '<table style="width: 100%">'
        for l in range(0, len(lines)):
            lines[l] = lines[l].replace('\r', '')
            new_line = self.line_processor(lines[l], l, False)
            #print(new_line)
            html = html + new_line

        html = html + '</table>'

        return html

    def toRallyMaster(self):
        lines = self.raw.split('\n')

        html = '<table style="width: 100%">'
        for l in range(0, len(lines)):
            lines[l] = lines[l].replace('\r', '')
            new_line = self.line_processor(lines[l], l, True)
            html = html + new_line

        html = html + '</table>'
        return html

    def toPCAFormat(self):
        lines = self.raw.split('\n')
        print('In toPCAFormat...')

        html = '<table border="1" style="width: 100%">'
        for l in range(0, len(lines)):
            lines[l] = lines[l].replace('\r', '')
            new_line = self.line_processor(lines[l], l, False)
            html = html + new_line

        html = html + '</table>'
        return html



@app.route('/', methods=('GET', 'POST'))
@app.route('/routes', methods=('GET', 'POST'))
def routes():
    global last_id
    conn = get_db_connection()
    print('routes: query db for all routes')
    routes = conn.execute('SELECT * from routes').fetchall()
    conn.close()

    """
    for r in routes:
        log_it(f"found {r['id']} {r['title']} in db")
    """

    if request.method == 'POST':
        # How do we know which button is pressed?
        # how do we convert a title to an ID?
        print('In routes for method POST')
        select = request.form.get('Route')
        theroute = request.form['Route']
        log_it(f'Requsested route /{str(select)}/')
        log_it(f'Selected route /{str(theroute)}/')

        # looks like id>title
        route_id = int(str(select).split('>')[0])

        if request.form['action'] == 'Edit':
            log_it(f'User wants to edit the route')
            last_id = route_id
            return redirect(url_for(f'edit', id=route_id))
        elif request.form['action'] == 'Printable':
            log_it(f'User wants to print the route')
            last_id = route_id
            return redirect(url_for(f'print_route', id=route_id))
        elif request.form['action'] == 'Copy':
            log_it(f'User wants to make a copy of the route')
            return redirect(url_for(f'add_new', id=route_id))
        elif request.form['action'] == 'Delete':
            log_it(f'User wants to delete the route')
            return redirect(url_for(f'delete_route', id=route_id))
        else:
            log_it(f"Don't know what the user wants to do")
            log_it(f"{request.form['action']}")

        return redirect(url_for(f'edit', id=route_id))

    print(f'render routes.html with {len(routes)} routes and last={last_id}')
    return render_template('routes.html', routes=routes, last_id=last_id)


@app.route('/routes/<int:route_id>')
def route_id(route_id):
    routes = get_route(route_id)
    return render_template('routes.html', routes=routes)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        if db_insert(request.form):
            return redirect(url_for(f'edit', id=id))

    return render_template('add.html', route=None)

@app.route('/add/<int:id>', methods=('GET', 'POST'))
def add_new(id):
    route = get_route(id)[0]

    if request.method == 'POST':
        if db_insert(request.form):
            return redirect(url_for(f'edit', id=id))
    return render_template('add.html', route=route)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    route = get_route(id)[0]

    # convert the row object to a dict so we can remove None values
    r = dict(route)
    for key in r:
        if r[key] == None:
            r[key] = ''
        if key == 'description':
            log_it(f'description = {r[key]}')
        if key == 'date':
            log_it(f'date = {r[key]}')
        if key == 'footer':
            log_it(f'footer = {r[key]}')
        if key == 'info':
            log_it(f'info = {r[key]}')

    if request.method == 'POST':
        title = request.form['title']
        owner = request.form['owner']
        date = request.form['date']
        description = request.form['description']
        info = request.form['info']
        route = request.form['route']
        distance = request.form['distance']
        duration = request.form['duration']
        map_url = request.form['map_url']
        footer = request.form['footer']

        if request.form['action'] == 'Submit':
            # update database record
            flash('Updating database entry')
            conn = get_db_connection()
            try:
                conn.execute('UPDATE routes SET title = ?, owner = ?, date = ?, '
                        'description = ?, info = ?, route = ?, distance = ?, '
                        'duration = ?, map_url = ?, footer = ?'
                        ' WHERE id = ?',
                        (title, owner, date, description, info, route, distance, duration, map_url, footer, id))
                conn.commit()
                flash(f'Route update success!')
            except sqlite3.Error as er:
                print(er.sqlite_errorcode)
                print(er.sqlite_errorname)
                flash(f'Route update failed! {er.sqlite_errorname}')

            conn.close()
            return redirect(url_for(f'edit', id=id))
        elif request.form['action'] == 'Print':
            return redirect(url_for(f'print_route', id=id))

    return render_template('add.html', route=r)

@app.route('/print/<int:id>')
def print_route(id):
    currentRoute = dict(get_route(id)[0])
    currentRoute['route'] = ROUTE(currentRoute['route'])

    return render_template('print.html', currentRoute=currentRoute)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/_get_description')
def get_description():

    route_id = request.args.get('route', 0)
    route = dict(get_route(route_id)[0])

    return route['description']

@app.route('/delete/<int:id>', methods=('GET', 'POST'))
def delete_route(id):
    if request.method == 'POST':
        if request.form['action'] == 'Delete':
            print(f'user confirmed they want to delete {id}')
        else:
            print(f'user confirmed they dont want to delete {id}')
        return redirect(url_for(f'routes'))

    route = dict(get_route(id)[0])
    info = {'id': id, 'title': route['title']}
    return render_template('delete.html', info=info)
