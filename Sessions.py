from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select, delete, ObjectNotFound
# from pathlib import Path
import json
import pprint
import secrets
from datetime import datetime, timedelta
import inspect

db = Database()

class Sessions(db.Entity):
    sessionid = PrimaryKey(str)
    datetime = Required(datetime)
    jsonstr = Optional(str)

db.bind(provider='sqlite', filename='./db/SessionsLog.db', create_db=False)
db.generate_mapping(create_tables=False)

def makeNewSessionID():
    return secrets.token_hex(10)

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

def _getdict(sessionID):
    if  not ifSessionExistsInDB(sessionID):
        return None
    else:
        with db_session:
            jsoninfo = Sessions[sessionID]
        value = jsoninfo.jsonstr
        if value is None or value == '':
            return None
        else:
            value = json.loads(value)
            return value

def getSessionValueFromDB(sessionID, name):
    pydict = _getdict(sessionID)
    if pydict == '':
        return None
    return pydict.get(name)

def initSessionInDB(sessionID):
    assert not ifSessionExistsInDB(sessionID)
    sessionDate = datetime.utcnow()
    with db_session:
        Sessions(sessionid=sessionID, datetime=sessionDate, jsonstr="{}")
    
def putSessionValueInDB(sessionID, name, value):
    pydict = _getdict(sessionID)
    if pydict is None:
        initSessionInDB(sessionID)
        pydict = {}
    pydict = pydict if pydict is not None and pydict != '' else {}
    pydict.update({name:value})
    jsondict = json.dumps(pydict)
    with db_session:
        sessionid = Sessions[sessionID]
        sessionid.jsonstr = jsondict

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

def initializeSessionsContainerInDB(sessionID):
    if ifSessionExistsInDB(sessionID):
        with db_session:
            Sessions[sessionID].delete()
    initSessionInDB(sessionID)




if __name__ == '__main__':
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
    purgeOldSessions()
