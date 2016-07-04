import json
import urllib2
import urllib

__author__ = 'nitesh'

client_id = "4"
client_secret = ""
scope = "https://picasaweb.google.com/data profile"
device_code = ""
access_token = ""
reresh_token = ""


def get_user_code_for_device():
    global device_code
    params = {'client_id': client_id, 'scope': scope}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://accounts.google.com/o/oauth2/device/code", data)
    response = urllib2.urlopen(req)
    json_string = response.read()
    json_obj = json.loads(json_string)
    device_code = json_obj['device_code']
    print json_obj


def get_tokens_for_user():
    params = {'client_id': client_id, 'client_secret': client_secret,
              'grant_type': 'http://oauth.net/grant_type/device/1.0', 'code': device_code}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://www.googleapis.com/oauth2/v4/token", data)
    response = urllib2.urlopen(req)
    json_string = response.read()
    json_obj = json.loads(json_string)
    print(json_obj)


def getUserProfileInfo():
    req = urllib2.Request("https://www.googleapis.com/plus/v1/people/me")
    req.add_header('Authorization', 'Bearer ' + access_token)
    resp = urllib2.urlopen(req)
    json_string = resp.read()
    json_obj = json.loads(json_string)
    name = json_obj['displayName']
    print name




#get_user_code_for_device()
#get_tokens_for_user()
getUserProfileInfo()