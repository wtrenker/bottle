from App import home, averages, chart
from bottle import Bottle, run, jinja2_template, default_app

def setup_routing (app):
    app.route('/', "GET", home)
    app.route('/averages', 'GET', averages)
    app.route('/chart' 'GET', chart)

# app = Bottle()
app = default_app()
setup_routing(app)

run(app, port=8200, host='localhost')
