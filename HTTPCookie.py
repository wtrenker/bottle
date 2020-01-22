from datetime import datetime, timedelta
from General import dateTimeStr

import pprint

sessionKey = 'glucose2'
sessionWeeks = 1

def getSessionCookie(request):
    sessionID = request.get_cookie(sessionKey)
    return sessionID

def setSessionCookie(response, sessionID):
    # naivenow = datetime.now()
    # pst = pytz.timezone("America/Vancouver")
    # now = pst.localize(naivenow)
    now = datetime.now()
    expires = now + timedelta(weeks=sessionWeeks)
    response.set_cookie(sessionKey, sessionID, expires=expires, httponly='on')

def deleteSessionCookie(response):
    response.delete_cookie(sessionKey)

'''

set_cookie(name, value, secret=None, digestmod=<built-in function openssl_sha256>, **options)
maxage  maximum age in seconds. (default: None)
expires  a datetime object or UNIX timestamp. (default: None)

zone = now.strftime('%Z')

'''

