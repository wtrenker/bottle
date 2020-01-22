from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select, delete
from datetime import datetime
# import Sessions
import syslog
# import General

db = Database()

class Log(db.Entity):
    datetime = PrimaryKey(datetime)
    sessionid = Optional(str)
    location = Optional(str)
    entry = Optional(str)

db.bind(provider='sqlite', filename='db/SessionsLog.db', create_db=False)
db.generate_mapping(create_tables=False)

import traceback

def log_backtrace():
    backtrace_frames = traceback.extract_stack()

    filename, line_number, function, code = backtrace_frames[0]
    print("msg = Backtrace: %s:%s: %s()\n" % (filename, line_number, function))
    detail = ""
    for frame in backtrace_frames[:-1]:
        filename, line_number, function, code = frame
        detail += "%s:%s: %s()\n" % (filename, line_number, function)
    print('detail = ')
    print(detail)

def putLog(location, line, sessionID=None):
    print(f'type of sessionID = {type(sessionID)}')
    sessionID = 'None' if sessionID is None else sessionID
    syslog.syslog(f'putLog: sessionID = {sessionID}, location = {location}, line = {line}')
    with db_session:
        if type(sessionID) != type(''):
            log_backtrace()
        Log(sessionid=sessionID, datetime=datetime.now(), location=location, entry=line)
log = putLog

def dumplog():
    print('--------- db log -----------')
    with db_session:
        qry = select((l.sessionid, l.datetime, l.location, l.entry) for l in Log).order_by(2)
        if qry.count() == 0:
            print('empty log')
        else:
            for logline in qry:
                print(logline)
    print('------- end of db log --------')

def emptylog():
    with db_session:
        delete(l for l in Log)


if __name__ == '__main__':
    # Sessions.initSession()
    log('1234', 'try this')
    # dumplog()
    # emptylog()
    # dumplog()


