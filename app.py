from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select
# from forms import SigninForm, DataEntryForm, SelectReadingForm, EditReadingForm, PickReadingForm
from GeneralFunctions import verify_password, decimalAverage
from collections import namedtuple
import time
import os
from pathlib import Path
import Chart
import Sessions
import System
import HTTPCookie
from GeneralFunctions import verify_password
from bottle import route, default_app, HTTPResponse, run, jinja2_view, url, get, post, request, html_escape,\
    response, redirect, debug, jinja2_template, MultiDict, post

import pprint

debug()

dbFileName = "glucose.db"
dbPath = Path(f'./db/{dbFileName}')
# dbPath = Path(dbFile)
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

def pickPrioritySessionID(request, urlIDFromFuctionParam):
    urlID = urlIDFromFuctionParam
    sessionID = None
    cookieID = HTTPCookie.getSessionIdCookieFromRequest(request)
    if cookieID is not None and cookieID != urlID and Sessions.ifSessionExistsInDB(cookieID):
        sessionID = cookieID
    if urlID is not None and Sessions.ifSessionExistsInDB(urlID):
        sessionID = urlID
    return sessionID

@get('/', name='home')
@jinja2_view('Home.jinja2', template_lookup=['templates'])
def home():
    requestData = dict(sessionID=Sessions.makeNewSessionID())
    requestData.update( dict(url=url, title='Blood Glucose'))
    return requestData

@get('/averages', name='averages')
@jinja2_view('Averages.jinja2', template_lookup=['templates'])
def averages():
    requestData = dict(url=url, title='Blood Glucose', timestamp=time.time())
    return requestData

@get('/chart', name='chart')
def chart():
    img = Chart.renderChart()
    resp = HTTPResponse(body=img, status=200)
    resp.set_header('content_type', 'image/png')
    return resp

@get('/admin', name='admin')
@get('/admin/<sessionID>', name='adminWithSessionid')
@jinja2_view('Admin.jinja2', template_lookup=['templates'])
def admin(sessionID=None):
    sessionID = pickPrioritySessionID(request, sessionID)

    Sessions.purgeOldSessions()

    if sessionID is None:
        sessionID = Sessions.makeNewSessionID()
        Sessions.initSessionInDB(sessionID)
        HTTPCookie.setSessionIdCookieInResponse(response, sessionID)
    Sessions.initializeSessionsContainerInDB(sessionID)
    Sessions.putSessionValueInDB(sessionID, 'isSignedOn', False)
    responseData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    return jinja2_template('Signon.jinja2', responseData, template_lookup=['templates'])

@get('/signon/<sessionID>', name='signon')
@jinja2_view('Signon.jinja2', template_lookup=['templates'])
def signon(sessionID):
    urlID = sessionID
    sessionID = pickPrioritySessionID(request, urlID)
    numberOfHeldReadings=numberOfPartials()
    Sessions.putSessionValueInDB(sessionID, "numberOfHeldReadings", numberOfHeldReadings)
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    respData.update(MultiDict(numberOfHeldReadings=numberOfHeldReadings))
    if Sessions.getSessionValueFromDB(sessionID, 'isSignedOn'):
        return jinja2_template('Admin.jinja2', respData, template_lookup=['templates'])
    else:
        return respData

@post('/signon', name='signonPost')
def signonPost():
    syscode = System.getCode()
    formcode = request.forms.get('code')
    isSignedOn = verify_password(syscode, formcode)
    sessionID = request.forms.sessionID
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    respData.update(MultiDict(numberOfHeldReadings=numberOfPartials()))
    if isSignedOn:
        Sessions.putSessionValueInDB(sessionID, 'isSignedOn', True)
        return jinja2_template('Admin.jinja2', respData, template_lookup=['templates'])
    else:
        return jinja2_template('Signon.jinja2', respData, template_lookup=['templates'])


@get('/enter/<sessionID>', name='enterData')
@jinja2_view('EnterReading.jinja2', template_lookup=['templates'])
def enter(sessionID):
    urlID = sessionID
    sessionID = pickPrioritySessionID(request, urlID)
    if not Sessions.ifSessionExistsInDB(sessionID):
        return jinja2_template('Signon.jinja2', template_lookup=['templates'])
    if Sessions.getSessionValueFromDB(sessionID, 'isSignedOn'):
        # form = request.forms()inspect.stack()[1][3])
        respData = MultiDict(url=url, title='Blood Glucose')
        respData.update(MultiDict(sessionID=sessionID))
        return respData
    else:
        return jinja2_view('Signon.jinja2', resoData, template_lookup=['templates'])

@post('/enter', name='enterPost')
def enterPost():
    return request.forms.date

@get('/select', name='selectReading')
def select(sessionID=None):
    requestData = dict(url=url, title='Blood Glucose')
    with db_session:
        heldReadings = Readings.select(lambda c: c.am is not None and c.pm is None).order_by(1)
        heldReadingsList = list(heldReadings)
    numberOfHeldReadings = len(heldReadingsList)
    if numberOfHeldReadings > 0:
        heldReadingDates = []
        index = 1
        for heldReading in heldReadingsList:
            heldReadingDates.append((f'D{index}', heldReading.date))
            index += 1
        requestData.update(dict(heldReadingDates=heldReadingDates))
        # Session.putSession('heldDates', heldReadingDates)
        return jinja2_view('SelectReading.jinja2', template_lookup=['templates'], **requestData)
    else:
        jinja2_view('NoneHeld.jinja2', template_lookup=['templates'], **requestData)


@get('/pick', name='pick')
@jinja2_view('PickReadingByDate.jinja2', template_lookup=['templates'])
def pick():
    return dict(url=url, title='Blood Glucose')



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
