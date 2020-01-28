from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select, IntegrityError, \
                     ObjectNotFound, max
# from forms import SigninForm, DataEntryForm, SelectReadingForm, EditReadingForm, PickReadingForm
from General import verify_password, decimalAverage
from collections import namedtuple
import time
import os
from pathlib import Path
import Chart
import Sessions
import System
import HTTPCookie
from General import verify_password, dbFileName, dateTimeStr
from bottle import route, default_app, HTTPResponse, run, jinja2_view, url, get, post, request, html_escape,\
    response, redirect, debug, jinja2_template, MultiDict, post
from General import isNone, isFloat
import pprint
from Log import putLog
from datetime import datetime

log = putLog

debug()

# response.log = []
# rla = response.log.append

dbPath = Path(f'./db/{dbFileName}')
# dbPath = Path(dbFile)

'''
db = Database()

class Readings(db.Entity):
    date = PrimaryKey(str)
    am = Required(float)
    pm = Optional(float)
    comment = Optional(str)
    average = Optional(float)

DAtE = 0
AM = 1
PM = 2
COMMENT = 3
AVERAGE = 4

db.bind(provider='sqlite', filename=str(dbPath), create_db=False)
db.generate_mapping(create_tables=False)

# session = Session.ThisSession()

def numberOfPartials():
    with db_session:
        return len(Readings.select(lambda c: c.am is not None and c.pm is None))
'''
@get('/chart', name='chart')
def chart():
    # log('chart', 'HTTPResponse')
    img = Chart.renderChart(request)
    resp = HTTPResponse(body=img, status=200)
    resp.set_header('content_type', 'image/png')
    return resp

# def setup_routing (app):
#     app.route('/chart', 'GET', chart)
#
# app = default_app()
# setup_routing(app)

@app.error(404)
def error404handler(error):
    f = request.fullpath
    respData = MultiDict(dict(f=f))
    return jinja2_template('405.jinja2', respData, template_lookup=['templates'])

@app.error(405)
def error405handler(error):
    f = request.fullpath
    respData = MultiDict(dict(f=f))
    return jinja2_template('405.jinja2', respData, template_lookup=['templates'])

@app.error(500)
def error500handler(error):
    return jinja2_template('500.jinja2', template_lookup=['templates'])



if __name__ == '__main__':
    run(host='localhost', port=8081, debug=True)








# from bottle import static_file
# @route('/static/<filename>')
# def server_static(filename):
#     return static_file(filename, root='/path/to/your/static/files')
#
# from bottle import redirect
# @route('/wrong/url')
# def wrong():
#     redirect("/right/url")
