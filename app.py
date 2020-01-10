from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select
# from forms import SigninForm, DataEntryForm, SelectReadingForm, EditReadingForm, PickReadingForm
from GeneralFunctions import verify_password, decimalAverage
from collections import namedtuple
import time
import os
from pathlib import Path
import Chart
# import System, Session, Log
from bottle import route, default_app, HTTPResponse, run, jinja2_view, url

import pprint

# dbFileName = "glucose.db"
# dbPath = Path(f'/home/bill/dbs/{dbFileName}')
# # dbPath = Path(dbFile)
# db = Database()
#
# class Readings(db.Entity):
#     date = PrimaryKey(str)
#     am = Required(float)
#     pm = Optional(float)
#     comment = Optional(str)
#     average = Optional(float)
#
# DAtE = 0
# AM = 1
# PM = 2
# COMMENT = 3
# AVERAGE = 4
#
# db.bind(provider='sqlite', filename=str(dbPath), create_db=False)
# db.generate_mapping(create_tables=False)

@route('/', name='home')
@jinja2_view('Home.jinja2', template_lookup=['templates'])
def home():
    return dict(url=url, title='Blood Glucose')

@route('/averages', name='averages')
@jinja2_view('Averages.jinja2', template_lookup=['templates'])
def averages():
    return dict(url=url, title='Blood Glucose')

@route('/chart', name='chart')
def chart():
    img = Chart.renderChart()
    resp = HTTPResponse(body=img, status=200)
    resp.set_header('content_type', 'image/png')
    return resp

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)

app = default_app()








# from bottle import static_file
# @route('/static/<filename>')
# def server_static(filename):
#     return static_file(filename, root='/path/to/your/static/files')
#
# from bottle import redirect
# @route('/wrong/url')
# def wrong():
#     redirect("/right/url")
