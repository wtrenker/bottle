from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select, IntegrityError, \
                     ObjectNotFound
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
from General import verify_password, dbFileName
from bottle import route, default_app, HTTPResponse, run, jinja2_view, url, get, post, request, html_escape,\
    response, redirect, debug, jinja2_template, MultiDict, post
from General import isNone
import pprint
from Log import putLog

log = putLog

debug()

# response.log = []
# rla = response.log.append

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

# @get('/', name='home')
# @jinja2_view('Home.jinja2', template_lookup=['templates'])
def home():
    # sessionID = Sessions.makeNewSessionID()
    # Sessions.initializeSession(sessionID, request, response)
    # respData = dict(sessionID=sessionID)
    respData = MultiDict(url=url, title='Blood Glucose')
    return jinja2_template('Home.jinja2', respData, template_lookup=['templates'])

# @get('/averages', name='averages')
# @jinja2_view('Averages.jinja2', template_lookup=['templates'])
def averages():
    # log('aveerges', 'Averages.jinja2')
    sessionID = HTTPCookie.getSessionCookie(request)
    respData = dict(url=url, title='Blood Glucose', timestamp=time.time(), sessionID=sessionID)
    return jinja2_template('Averages.jinja2', respData, template_lookup=['templates'])

# @get('/chart', name='chart')
def chart():
    # log('chart', 'HTTPResponse')
    img = Chart.renderChart()
    resp = HTTPResponse(body=img, status=200)
    resp.set_header('content_type', 'image/png')
    return resp

def adminCommon(request, response, sessionID=None):
    Sessions.purgeOldSessions()
    sessionID = Sessions.initializeSession(sessionID, request, response)
    Sessions.putSessionValueInDB(sessionID, 'currentDB', str(dbPath))
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    respData.update(MultiDict(numberOfHeldReadings=numberOfPartials()))
    isSignedOn = Sessions.getSessionValueFromDB(sessionID, 'isSignedOn')
    if isSignedOn:
        template = jinja2_template('Admin.jinja2', respData, template_lookup=['templates'])
    else:
        template = jinja2_template('Signon.jinja2', respData, template_lookup=['templates'])
    log('adminCommon', 'made new session', sessionID=sessionID)
    return template

# @get('/admin', name='admin')
def adminNoID():
    template = adminCommon(request, response)
    return template

# @get('/admin/<sessionID>', name='adminWithSessionid')
def adminWithSessionid(sessionID):
    template = adminCommon(request, response, sessionID=sessionID)
    return template

# @get('/signon/<sessionID>', name='signon')
# @jinja2_view('Signon.jinja2', template_lookup=['templates'])
def signon(sessionID):
    numberOfHeldReadings=numberOfPartials()
    Sessions.putSessionValueInDB(sessionID, "numberOfHeldReadings", numberOfHeldReadings)
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    respData.update(MultiDict(numberOfHeldReadings=numberOfHeldReadings))
    if Sessions.getSessionValueFromDB(sessionID, 'isSignedOn'):
        return jinja2_template('Admin.jinja2', respData, template_lookup=['templates'])
    else:
        return jinja2_template('Signon.jinja2', respData, template_lookup=['templates'])

# @post('/signon', name='signonPost')
def signonPost():
    sessionID = request.forms.sessionID
    if isNone(sessionID):
        sessionID = HTTPCookie.getSessionCookie(request)
    syscode = System.getCode()
    formcode = request.forms.get('code')
    isSignedOn = verify_password(syscode, formcode)
    Sessions.putSessionValueInDB(sessionID, 'isSignedOn', isSignedOn)
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    respData.update(MultiDict(numberOfHeldReadings=numberOfPartials()))
    if isSignedOn:
        return jinja2_template('Admin.jinja2', respData, template_lookup=['templates'])
    else:
        respData.update(MultiDict(tryAgain=True))
        return jinja2_template('Signon.jinja2', respData, template_lookup=['templates'])


# @get('/enter/<sessionID>', name='enterData')
# @jinja2_view('EnterReading.jinja2', template_lookup=['templates'])
def enter(sessionID):
    sessionID = Sessions.initializeSession(sessionID, request, response)
    respData = MultiDict(url=url, title='Blood Glucose')
    isSignedOn = Sessions.getSessionValueFromDB(sessionID, 'isSignedOn')
    respData.update(MultiDict(sessionID=sessionID, numberOfHeldReadings=numberOfPartials()))
    respData.update(MultiDict(dbFileName=dbFileName))
    if isSignedOn:
        return jinja2_template('EnterReading.jinja2', respData, template_lookup=['templates'])
    else:
        return jinja2_template('Signon.jinja2', respData,  template_lookup=['templates'])

# @post('/enter', name='enterPost')
def enterPost():
    rf = request.forms
    formDate = rf.date
    formAM = rf.am
    formPM = rf.pm
    formPM = None if formPM == '' else formPM
    formNote = rf.comment
    sessionID = HTTPCookie.getSessionCookie(request)
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    respData.update(MultiDict(numberOfHeldReadings=numberOfPartials()))
    alreadyEntered = False
    try:
        with db_session:
            Readings(date=formDate, am=formAM, pm=formPM, comment=formNote)
    except (IntegrityError, Exception):
        alreadyEntered = True
    if alreadyEntered:
        respData.update(MultiDict(editDate=formDate, alreadyEntered=True))
        respData.update(MultiDict(alreadyEntered=True))
        return jinja2_template('EnterReading.jinja2', respData, template_lookup=['templates'])
    respData.update(MultiDict(numberOfHeldReadings=numberOfPartials()))
    return jinja2_template('Admin.jinja2', respData, template_lookup=['templates'])

# @get('/select/<sessionID>', name='selectReading')
def selectReadings(sessionID=None):
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    if sessionID is None or not Sessions.ifSessionExistsInDB(sessionID):
        return jinja2_template('Home.jinja2', respData, template_lookup=['templates'])
    Sessions.putSessionValueInDB(sessionID, 'sessionIDtoSelect', sessionID)

    if not Sessions.getSessionValueFromDB(sessionID, 'isSignedOn'):
        return jinja2_template('Signon.jinja2', respData, template_lookup=['templates'])

    with db_session:
        heldReadings = Readings.select(lambda c: c.am is not None and c.pm is None).order_by(1)
        heldReadingsList = list(heldReadings)
    numberOfHeldReadings = len(heldReadingsList)
    respData.update(MultiDict(numberOfHeldReadings=numberOfHeldReadings))
    if numberOfHeldReadings > 0:
        heldReadingDates = []
        index = 1
        for heldReading in heldReadingsList:
            heldReadingDates.append((f'D{index}', heldReading.date))
            index += 1

        respData.update(MultiDict(heldReadingDates=heldReadingDates))
        respData.update(MultiDict(heldData=None))
        return jinja2_template('SelectReading.jinja2', respData, template_lookup=['templates'])
    else:
        return jinja2_template('NoneHeld.jinja2', respData, template_lookup=['templates'])

# @post('/select', name='selectPost')
# @jinja2_view('EditReading.jinja2', template_lookup=['templates'])
def selectPost():
    rf = request.forms
    sessionID = rf.sessionID
    selectedDate = rf.selectedDate
    respData = MultiDict(url=url, title='Blood Glucose', sessionID=sessionID)
    with db_session:
        reading = Readings[selectedDate]
    form = MultiDict()
    form.date = reading.date
    form.am = reading.am
    form.pm = reading.pm if reading.pm is not None else ''
    form.comment = reading.comment if reading.comment is not None else ''
    respData.update(MultiDict(form=form, dbFileName=dbFileName))
    return jinja2_template('EditReading.jinja2', respData, template_lookup=['templates'])


# @post('/update', name='editReading')
# @jinja2_view('UpdateDone.jinja2', template_lookup=['templates'])
def edit():
    respData = MultiDict(url=url, title='Blood Glucose')
    rf = request.forms
    with db_session:
        reading = Readings[rf.date]
        if rf.pm != '':
            reading.pm = rf.pm
        if rf.comment != '':
            reading.comment = rf.comment
    return jinja2_template('UpdateDone.jinja2', respData, template_lookup=['templates'])

# @get('/pick', name='pick')
# @jinja2_view('PickReadingByDate.jinja2', template_lookup=['templates'])
# def pick():
#     return dict(url=url, title='Blood Glucose')

def setup_routing (app):
    app.route('/', "GET", home)
    app.route('/home', "GET", home)
    app.route('/averages', 'GET', averages)
    app.route('/chart', 'GET', chart)
    app.route('/admin', 'GET', adminNoID)
    app.route('/admin/<sessionID>', 'GET', adminWithSessionid)
    app.route('/signon/<sessionID>', 'GET', signon)
    app.route('/signon', 'POST', signonPost)
    app.route('/enter/<sessionID>', "GET", enter)
    app.route('/enter', 'POST',enterPost)
    app.route('/select/<sessionID>', 'GET', selectReadings)
    app.route('/select', 'POST', selectPost)
    app.route('/update', 'POST', edit)

app = default_app()
setup_routing(app)



if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)








# from bottle import static_file
# @route('/static/<filename>')
# def server_static(filename):
#     return static_file(filename, root='/path/to/your/static/files')
#
# from bottle import redirect
# @route('/wrong/url')
# def wrong():
#     redirect("/right/url")
