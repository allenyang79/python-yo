import email
import json
import logging
import math
import smtplib
import time
import base64
from string import maketrans
from flask import Flask
from flask import request
from flask.ext.login import current_user

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
def force_float(x, defaultValue=0):
    try:
        return float(x)
    except:
        return defaultValue
def force_int(x, defaultValue=0):
    try:
        return int(x)
    except:
        return defaultValue

def isObjectModified(x, y):
    return json.dumps(x or {}, sort_keys=True) != json.dumps(y, sort_keys=True)


def loadObject(key, default="{}"):
    try:
        return json.loads(request.values.get(key, default))
    except:
        return json.loads(default)


def loadArray(key, default="[]"):
    try:
        return json.loads(request.values.get(key, default))
    except:
        return json.loads(default)


def getTaiwanTomorrowTS():
    return getTWDayBeginTS(time.time()) + 86400


def getTaiwanTodayTS():
    return getTWDayBeginTS(time.time())


def getTWDayBeginTS(ts):
    return getTZDayBeginTS(ts, 8)

def getTZDayBeginTS(timestamp, timezone):
    back_to_day_begin = (timestamp + 3600*timezone) % 86400
    return int(timestamp - back_to_day_begin)


# Use binary search to find the key in the list
# Return the index where the list remain sorted after item inserts.
def binarySearch(lst, key, func=lambda x: x):
    low = 0
    high = len(lst) - 1

    while high >= low:
        mid = (low + high) // 2
        if key < func(lst[mid]):
            high = mid - 1
        elif key == func(lst[mid]):
            return mid
        else:
            low = mid + 1
    return low

def sendEmail(app, from_user, to_list, subject, content_html, cc_list=[]):
    msg = email.MIMEMultipart.MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_user
    msg['To'] = ", ".join(to_list)
    msg['Cc'] = ", ".join(cc_list)
    msg.attach(email.mime.text.MIMEText(content_html, 'html'))

    try:
        s = smtplib.SMTP(app.config['SMTP_HOST'])
        if app.config['SMTP_DO_SENT']:
            s.sendmail(msg['From'], to_list + cc_list, msg.as_string())
        else:
            s.sendmail(msg['From'], ['Patrick Chen <springgod@appier.com>'], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        logger.error('Send daily creative list failed: msg: %s', msg.as_string())
        logger.error(str(e))
        return False


# Extract params from request object based on rules. Not listed key will not be outputed.
#
# There might be a dict with key, 'inputConfig' in the setting.
# The default setting of inputConfig is
#   {
#       'mustReject':False,
#       'mustAccept':False,
#       'needPermission':[],
#       'type': 'str'
#   }
# rule format:
#   { field: setting object}
#   setting object:
#       type: "str"(default), "int", "float", "json", 'boolean'
#       default: default value or default value fucntion // if this field is not provided, the key will not be added.
#
#       possibleValue: []
#       // if conflict,  Reject > Accept > Permission
#       mustReject: boolean
#       mustAccept: boolean
#       needPermission: list of permission
def extractRequest(rules):
    ret = {}
    for field, rule in rules.iteritems():
        conf = rule.get('inputConfig', {})
        if conf.get("mustReject", False):
            continue
        if conf.get("mustAccept", False):
            pass
        elif current_user.has_permission(conf.get("needPermission", [])):
            pass
        else:
            continue

        if field in request.values:
            t = conf.get('type', 'str')
            if t == "int":
                ret[field] = force_int(request.values[field])
            elif t == "float":
                ret[field] = force_float(request.values[field])
            elif t == "json":
                ret[field] = loadObject(field)
            elif t == 'boolean':
                if request.values.get(field) == 'true':
                    ret[field] = True
                else:
                    ret[field] = False
            else: # default to str
                ret[field] = request.values[field]
            if 'possibleValue' in conf:
                if ret[field] not in conf['possibleValue']:
                    del ret[field]
        elif "default" in conf:
            if hasattr(conf["default"], '__call__'):
                ret[field] = conf["default"]()
            else:
                ret[field] = conf["default"]
    return ret

#
# Make diff object and append to history
#
# All fields(not only defined fields) will be processed.
# There might be a dict with key, 'historyConfig' in the setting.
# The default setting of outputConfig is {'skip':False, 'func':'str'}
# rule format:
#   { field: setting object}
#   setting object:
#     skip: True to skip diff process
#     func: function code or function
#       function code supports following
#         direct(default)
#         flat object: for object that has only one layer
#         set: convert array into set and then do the diff
#       or a function(origin, updated) 
#       The func should return None if nothing changed.
#       Otherwise, return the dict that will be recorded.
#       
def makeDiffHistory(origin, updated, config, history_key='history'):
    all_fields = set(origin.keys()).union(set(updated.keys()))
    def flatFunc(x, y):
        added = {}
        removed = {}
        origin = {}
        updated = {}
        for key in x.keys():
            if key not in y:
                removed[key] = x[key]
            elif x[key] != y[key]:
                origin[key] = x[key]
                updated[key] = y[key]
        for key in y.keys():
            if key not in x:
                added[key] = y[key]
        if len(added) + len(removed) + len(origin) + len(updated) == 0:
            return None
        else:
            return {
                'added': added,
                'removed': removed,
                'origin': origin,
                'updated': updated
            }
    def directFunc(x, y):
        if x==y:
            return None
        else:
            return {
                'from': x,
                'to': y
            }
    def setFunc(x, y):
        if set(x) == set(y):
            return None
        else:
            return {
                'added': [i for i in set(y) if i not in x],
                'removed': [i for i in set(x) if i not in y]
            }

    records = []
    for key in all_fields:
        if key == history_key:
            continue
        conf = config.get(key, {}).get('historyConfig', {})
        if conf.get('skip', False):
            continue
        df = conf.get('func', 'direct')
        if df is 'direct':
            df = directFunc
        elif df is 'flat':
            df = flatFunc
        elif df is 'set':
            df = setFunc

        try:
            row = df(origin.get(key), updated.get(key))
        except:
            row = {
                'errorMsg': 'error on process diff',
                'from': origin.get(key),
                'to': updated.get(key)
            }
        if row is not None:
            row['key'] = key
            records.append(row)
    if len(records) > 0:
        if history_key not in updated:
            updated[history_key] = []
        updated[history_key].append({
            'updated_at': int(time.time()),
            'updated_by': current_user.username,
            'v': 1,
            'changes': records
            })

#
# Use this function to format return object.
# This function has following features:
# 1. Translate _id to a specific key
# 2. Filter out field by permission
# Only defined key will be return. Config is a dictionary of (field , setting)
# There might be a dict with key, 'outputConfig' in the setting.
# The default setting of outputConfig is {'alwaysReturn':True}
# Options:(check sequentially)
#    neverReturn: boolean
#    alwaysReturn: boolean
#    needPermission: array of permissions
#
def formatReturnObject(
        instance=None,
        array=None,
        config=None,
        instanceReadPermission=lambda x:True,
        instanceWritePermission=lambda x:True):
    def parseInstance(inst):
        ret = {}
        for field, rule in config.iteritems():
            conf = rule.get('outputConfig', {})
            if conf.get("neverReturn", False):
                continue
            if conf.get("alwaysReturn", False):
                pass
            elif current_user.has_permission(conf.get("needPermission", [])):
                pass
            else:
                continue
            if conf.get('primary_key', False):
                if '_id' not in inst:
                    continue
                else:
                    ret[field] = inst['_id']
            else:
                if field not in inst:
                    if "default" in conf:
                        if hasattr(conf["default"], '__call__'):
                            ret[field] = conf["default"]()
                        else:
                            ret[field] = conf["default"]
                    else:
                        continue
                else:
                    ret[field] = inst[field]
        ret['__write_permission'] = instanceWritePermission(inst)
        if not instanceReadPermission(inst):
            return None
        else:
            return ret
    if array is None:
        return parseInstance(instance)
    else:
        ret_ary = []
        for instance in array:
            ins = parseInstance(instance)
            if ins is not None:
                ret_ary.append(ins)
        return ret_ary


#
# Our encryption library for external data
#
ENCODE_TABLE = maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
                         "dT40GSbLulkKo725MtnrIi8Hw3cUZJCe6N1qfgYjaEXF-W9BxVyPRsmDQz_pAOhv")
DECODE_TABLE = maketrans("dT40GSbLulkKo725MtnrIi8Hw3cUZJCe6N1qfgYjaEXF-W9BxVyPRsmDQz_pAOhv",
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
def b64Encrypt(s):
    return base64.urlsafe_b64encode(s).replace("=", "").translate(ENCODE_TABLE)

def b64Decrypt(s):
    s = str(s).translate(DECODE_TABLE)
    if len(s) % 4 != 0:
        s += '='*(4 - len(s) % 4)
    #logging.debug('after decrypt, before b64decode: s:%s', s)
    return base64.urlsafe_b64decode(s)

