import json
import urllib2
import urllib
import xml.dom.minidom

__author__ = 'nitesh'

client_id = ""
client_secret = ""
scope = "https://picasaweb.google.com/data profile"
device_code = ""
access_token = ""
refresh_token = ""


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


def get_access_token_using_refresh_token():
    global access_token
    print "Refreshing stale token"
    params = {'client_id': client_id, 'client_secret': client_secret,
              'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://www.googleapis.com/oauth2/v4/token", data)
    response = urllib2.urlopen(req)
    json_string = response.read()
    json_obj = json.loads(json_string)
    access_token = json_obj['access_token']
    print(json_obj)


def make_request(req, data=None):
    req.add_header('Authorization', 'Bearer ' + access_token)
    try:
        resp_stream = urllib2.urlopen(req, data)
        response = resp_stream.read()
        return response
    except urllib2.HTTPError, e:
        if e.code == 401:
            get_access_token_using_refresh_token()
            response = make_request(req)
            return response
        elif e.code == 403:
            get_user_code_for_device()
            return ""


def get_user_profile_info():
    req = urllib2.Request("https://www.googleapis.com/plus/v1/people/me")
    json_string = make_request(req)
    json_obj = json.loads(json_string)
    name = json_obj['displayName']
    print name


def get_text(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def parse_xml_for_albums(xmlstr):
    entries = []
    dom = xml.dom.minidom.parseString(xmlstr)
    feed = dom.getElementsByTagName('feed')
    if len(feed) > 0:
        feed = feed[0]
        entryNodes = feed.getElementsByTagName('entry')
        for entryNode in entryNodes:
            idNode = entryNode.getElementsByTagName('gphoto:id')
            titleNode = entryNode.getElementsByTagName('title')
            if len(idNode):
                album_id = get_text(idNode[0].childNodes)
                title = get_text(titleNode[0].childNodes)
                entries.append({'id': album_id, 'title': title})

    print entries
    return entries


def get_user_album_list():
    req = urllib2.Request("https://picasaweb.google.com/data/feed/api/user/default")
    xml_string = make_request(req)
    album_list = parse_xml_for_albums(xml_string)
    for album in album_list:
        print album['title']


def parse_xml_for_photos(xmlstr):
    photos = []
    dom = xml.dom.minidom.parseString(xmlstr)
    feed = dom.getElementsByTagName('feed')
    if len(feed) > 0:
        feed = feed[0]
        entryNodes = feed.getElementsByTagName('entry')
        for entryNode in entryNodes:
            idNode = entryNode.getElementsByTagName('content')
            titleNode = entryNode.getElementsByTagName('title')
            if len(idNode):
                url = idNode[0].getAttribute('src')
                title = get_text(titleNode[0].childNodes)
                photos.append({'url': url, 'title': title})

    return photos


def get_photo_list_for_album(album_id):
    req = urllib2.Request("https://picasaweb.google.com/data/feed/api/user/default/albumid/" + album_id + '?imgmax=d')
    xml_string = make_request(req)
    photo_list = parse_xml_for_photos(xml_string)
    for photo in photo_list:
        print photo['url']


#get_user_code_for_device()
#get_tokens_for_user()
#get_user_profile_info()
#get_access_token_using_refresh_token()
#get_user_album_list()
#get_photo_list_for_album('')
