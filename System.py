from pony.orm import Database, Optional, Required, PrimaryKey, db_session, sql_debug, select

db = Database()

class System(db.Entity):
    name = PrimaryKey(str)
    value = Optional(str)

db.bind(provider='sqlite', filename='db/SessionsLog.db', create_db=False)
db.generate_mapping(create_tables=False)

def getCode():
    with db_session:
        codeobj = System['code']
    codesstr = codeobj.value
    if codesstr is None or codesstr == '':
        return ''
    return codesstr

# def getSessionID():
#     with db_session:
#         codeobj = System['sessionid']
#     codesstr = codeobj.value
#     if codesstr is None or codesstr == '':
#         return None
#     return codesstr


if __name__ == "__main__":
    print(getCode())
