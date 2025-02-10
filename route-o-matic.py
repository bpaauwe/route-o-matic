from flask import Flask
from flask import render_template
from flask import request, url_for, flash, redirect
from waitress import serve
from mydb import RouteDB


app = Flask(__name__)
app.config['SECRET_KEY'] = '3asdfki5489907asLJO8dka378'
routedb = RouteDB({})
last_id = 0


@app.context_processor
def inject_verions():
    return dict(version="Version 3.0.0", date="02/08/2025")

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
            text = text.replace(' T ','<b> T </b>')
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
            elif (miles == 'RM' or miles == 'rm') and flag:
                new_line = td_l.format(num) + td_n.format('') + td_i.format(text) + td_x.format(extra)
            elif miles == 'RM' or miles == 'rm':
                # ignore these lines
                new_line = ''
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

    print('routes: query db for all routes')
    routes = routedb.get_routes()

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
        print(f'Requsested route /{str(select)}/')
        print(f'Selected route /{str(theroute)}/')

        # looks like id>title
        route_id = int(str(select).split('>')[0])

        if request.form['action'] == 'Edit':
            print(f'User wants to edit the route')
            last_id = route_id
            return redirect(url_for(f'edit', id=route_id))
        elif request.form['action'] == 'Printable':
            print(f'User wants to print the route')
            last_id = route_id
            return redirect(url_for(f'print_route', id=route_id, format="HTML"))
        elif request.form['action'] == 'Copy':
            print(f'User wants to make a copy of the route')
            return redirect(url_for(f'add_new', id=route_id))
        elif request.form['action'] == 'Delete':
            print(f'User wants to delete the route')
            return redirect(url_for(f'delete_route', id=route_id))
        else:
            print(f"Don't know what the user wants to do")
            print(f"{request.form['action']}")

        return redirect(url_for(f'edit', id=route_id))

    print(f'render routes.html with {len(routes)} routes and last={last_id}')
    return render_template('routes.html', routes=routes, last_id=last_id)


@app.route('/routes/<int:route_id>')
def route_id(route_id):
    routes = routedb.get_route(route_id)
    return render_template('routes.html', routes=routes)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        route_id = routedb.insert_route(request.form)
        if route_id > 0:
            # we need the id of the route we just inserted
            return redirect(url_for(f'edit', id=route_id))

    return render_template('add.html', route=None)

@app.route('/add/<int:id>', methods=('GET', 'POST'))
def add_new(id):
    route = routedb.get_route(id)[0]

    if request.method == 'POST':
        # should this route back to original or copy?  currently it goes to original
        if routedb.insert_route(request.form):
            return redirect(url_for(f'edit', id=id))
    return render_template('add.html', route=route)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    route = routedb.get_route(id)[0]

    # convert the row object to a dict so we can remove None values
    r = dict(route)
    for key in r:
        if r[key] == None:
            r[key] = ''
        if key == 'description':
            print(f'description = {r[key]}')
        if key == 'date':
            print(f'date = {r[key]}')
        if key == 'footer':
            print(f'footer = {r[key]}')
        if key == 'info':
            print(f'info = {r[key]}')

    if request.method == 'POST':
        if request.form['action'] == 'Submit':
            # update database record
            flash('Updating database entry')
            routedb.update_route(id, request.form)
            return redirect(url_for(f'edit', id=id))
        elif request.form['action'] == 'Print':
            select = request.form.get('printFormat')
            print(f"User wants to print using {select}")
            return redirect(url_for(f'print_route', id=id, format=select))

    return render_template('add.html', route=r)

@app.route('/print/<int:id>/<string:format>')
def print_route(id, format):
    currentRoute = dict(routedb.get_route(id)[0])
    currentRoute['route'] = ROUTE(currentRoute['route'])

    return render_template('print.html', currentRoute=currentRoute, format=format)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/_get_description')
def get_description():

    route_id = request.args.get('route', 0)
    route = dict(routedb.get_route(route_id)[0])

    return route['description']

@app.route('/delete/<int:id>', methods=('GET', 'POST'))
def delete_route(id):
    if request.method == 'POST':
        if request.form['action'] == 'Delete':
            print(f'user confirmed they want to delete {id}')
            routedb.delete_route(id)
        else:
            print(f'user confirmed they dont want to delete {id}')
        return redirect(url_for(f'routes'))

    route = dict(routedb.get_route(id)[0])
    info = {'id': id, 'title': route['title']}
    return render_template('delete.html', info=info)


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    serve(app, host='0.0.0.0', port=8200)

