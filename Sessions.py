from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select, delete, ObjectNotFound
from bottle import response

# from pathlib import Path
import json
import pprint
import secrets
from datetime import datetime, timedelta
import inspect
import HTTPCookie
from General import isNone
import syslog
from Log import log

db = Database()

class Sessions(db.Entity):
    sessionid = PrimaryKey(str)
    datetime = Required(datetime)
    jsonstr = Optional(str)

db.bind(provider='sqlite', filename='db/SessionsLog.db', create_db=False)
db.generate_mapping(create_tables=False)

#########################################################################

def makeNewSessionID():
    return secrets.token_hex(10)

#########################################################################

def getSessionIdFromDb(sessionID):
    try:
        with db_session:
            _ = Sessions[sessionID]
    except ObjectNotFound:
        return None
    else:
        return sessionID

def ifSessionExistsInDB(sessionID):
    return True if getSessionIdFromDb(sessionID) is not None else False

###########################################################################


###########################################################################

def _getdict(sessionID):
    if  not ifSessionExistsInDB(sessionID):
        return None
    else:
        with db_session:
            jsoninfo = Sessions[sessionID]
        value = jsoninfo.jsonstr
        if isNone(value) or value == '':
            return None
        else:
            value = json.loads(value)
            return value

def getSessionValueFromDB(sessionID, name):
    pydict = _getdict(sessionID)
    if pydict == '':
        return None
    return pydict.get(name)

def putSessionValueInDB(sessionID, name, value):
    if sessionID is None:
        print(f'is None, {name}  {value}')
        exit()
    pydict = _getdict(sessionID)
    if pydict is None:
        # initSessionInDB(sessionID)
        pydict = {}
    else:
        pydict = pydict if pydict is not None and pydict != '' else {}
    pydict.update({name:value})
    jsondict = json.dumps(pydict)
    with db_session:
        session = Sessions[sessionID]
        session.jsonstr = jsondict

##################################################################################

def deleteSession(sessionID, request, response):
    log('deleteSession', f'sessionID = {sessionID}')
    with db_session:
        try:
            Sessions[sessionID].delete()
        except ObjectNotFound:
            pass
    cookie = HTTPCookie.getSessionCookie(request)
    if cookie == sessionID:
        HTTPCookie.deleteSessionCookie(response)

def _initializeDbSession(sessionID):
    sessionDate = datetime.utcnow()
    with db_session:
        Sessions(sessionid=sessionID, datetime=sessionDate, jsonstr="{}")

def initializeSession(existingSessionID, request, response):
    print(f'initializeSession: type of sessionID = {type(existingSessionID)}')
    log('initializeSession', f'oldSessionID = {existingSessionID}', sessionID=existingSessionID)
    print(type(existingSessionID))
    if  isNone(existingSessionID):
        sessionID = makeNewSessionID()
    else:
        sessionID = existingSessionID
    if not ifSessionExistsInDB(sessionID):
        # response.log.append(f'initializeSession: ifSessionExistsInDB = True<br/>')
        # deleteSession(oldSessionID, request, response)  # remove session from db and cookie (failsafe)
        # newSessionID =  makeNewSessionID()
        _initializeDbSession(sessionID)
    if HTTPCookie.getSessionCookie(request) != sessionID:
        HTTPCookie.setSessionCookie(response, sessionID)
    # cookieID = HTTPCookie.getSessionCookie(request)
    # response.log.append(f'initializeSession: after initialization of newSessionID getSessionCookie = {cookieID}<br/>')
    # else:
    #     response.log.append(f'initializeSession: cookieID is not in DB<br/>')
    #     HTTPCookie.setSessionCookie(response, sessionID)
    #     response.log.append(f'initializeSession: after setSessionCookie to sessionID, getSessionCookie = {HTTPCookie.getSessionCookie(request)}<br/>')
    # if cookieID and cookieID != sessionID:
    #     HTTPCookie.deleteSessionCookie(response)
    #     HTTPCookie.setSessionCookie(response, cookieID)
    #     response.log.append(f'initializeSession: after setSessionCookie, getSessionCookie = {HTTPCookie.getSessionCookie(request)}<br/>')
    log('initializeSession', f'exit', sessionID=sessionID)
    return sessionID

######################################################################################

# def reInitializeSessionsCookie(sessionID, request, response):
#     deleteSession(sessionID, request, response)
#     pass

def purgeOldSessions():
    now = datetime.utcnow()
    delta =  timedelta(minutes=60)
    with db_session:
        for session in select((s.sessionid, s.datetime) for s in Sessions):
            if (now - session[1]) > delta:
                Sessions[session[0]].delete()

def _dumpsessions():
    print('--------- sessions -----------')
    with db_session:
        qry = select((s.sessionid, s.datetime, s.jsonstr) for s in Sessions).order_by(2)
        if qry.count() == 0:
            print('no sessions')
        else:
            for sessline in qry:
                print(sessline)
    print('------- end of sessions --------')

def _emptysessions():
    with db_session:
        delete(s for s in Sessions)

##############################################################################################


def _currentSessionLocation(sessionID):
    inCookie = inDB = False
    location = None

def SessionFactory(request, response, urlIDFromFuctionParam):
    ''' returns the highest priority existing session ID
    or creates a new session and returns that ID
    also returns the location of the session ID'''
    urlID = urlIDFromFuctionParam
    sessionID = where = None
    inDB = inCookie = False
    if urlID:
        if ifSessionExistsInDB(urlID):
            sessionID = urlID
            where = "db"
            inDB = True
        else:
            cookieID = HTTPCookie.getSessionCookie(request)
            if not isNone(cookieID) and cookieID != urlID and ifSessionExistsInDB(cookieID):
                sessionID = cookieID
                where = "cookie"
                inCookie = True
                inDB = True
            else:
                sessionID = urlID
                where = 'url'
                inDB = False
                inCookie = False
    else:
        where = 'new'
    if where in {'new', 'url'}:
        sessionID = makeNewSessionID()
        initializeSession(sessionID, request, response)
    return sessionID, where




if __name__ == '__main__':
    sID = makeNewSessionID()
    print(f'type of sID = [{type(sID)}')
    pass
    # _emptysessions()
    # sessionID = makeNewSessionID()
    # print(f'ThisSession.id = {sessionID}')
    # RegisterSession(sessionID)
    #
    # exit()

    # sessionID = '08e584ef6b71c4a7993c'
    # if ifSessionExistsInDB(sessionID):
    #     print(f'{sessionID} is in DB')
    #     putSessionValueInDB(sessionID, 'name', 'Billy')
    # # _dumpsessions()
    #     print(getSessionValueFromDB(sessionID, 'name'))
    # else:
    #     print(f'{sessionID} is NOT in DB')
    #     sessionID = makeNewSessionID()
    #     print(f'new sessionID = {sessionID}')
    #     putSessionValueInDB(sessionID, "name", "Janice")
    # purgeOldSessions()

    # deleteSession('snorg')

