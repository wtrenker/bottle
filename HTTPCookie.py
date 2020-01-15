from datetime import datetime, timedelta
from GeneralFunctions import dateTimeStr

import pprint

sessionKey = 'glucose2'
sessionWeeks = 1

def getSessionIdCookieFromRequest(request):
    sessionID = ''  #ensure the variable is defined incase the following try fails
    try:
        sessionID = request.get_cookie(sessionKey)
    except:
        sessionID = NoNe
    # sessionID = sessionID if sessionID is not None else ''  #ensure result is not None
    return sessionID

def setSessionIdCookieInResponse(response, sessionID):
    # naivenow = datetime.now()
    # pst = pytz.timezone("America/Vancouver")
    # now = pst.localize(naivenow)
    now = datetime.now()
    expires = now + timedelta(weeks=sessionWeeks)
    expires = dateTimeStr(expires)
    response.set_cookie(sessionKey, sessionID, expires=expires)

'''

set_cookie(name, value, secret=None, digestmod=<built-in function openssl_sha256>, **options)
maxage  maximum age in seconds. (default: None)
expires  a datetime object or UNIX timestamp. (default: None)

zone = now.strftime('%Z')

'''

# expires = dateTimeStr(datetime.now())
# print(expires)
