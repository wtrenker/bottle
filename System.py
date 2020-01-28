from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select

db = Database()

class System(db.Entity):
    name = PrimaryKey(str)
    value = Optional(str)

db.bind(provider='sqlite', filename='db/SessionsLog.db', create_db=False)
db.generate_mapping(create_tables=False)

def _get(name):
    with db_session:
        dbobj = System[name]
    returnstr = dbobj.value
    if returnstr is None or returnstr == '':
        return ''
    return returnstr

def getCode():
    return _get('code')

def getSessionID():
    return _get('sessionid')

def getLastReadingDateStr():
    return _get('lastreadingdatestr')

def _put(name, value):
    with db_session:
        dbobj = System[name]
        dbobj.value = value

def putCode(value):
    _put('code', value)

def putSessionID(value):
    _put('sessionid', value)

def putLastReadingDateStr(value):
    _put('lastreadingdatestr', value)



if __name__ == "__main__":
    putLastReadingDateStr('12345')
    print(getLastReadingDateStr())