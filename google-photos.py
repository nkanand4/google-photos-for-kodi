import json
import urllib2
import urllib
import xml.dom.minidom

__author__ = 'nitesh'

client_id = ""
client_secret = ""
scope = "https://picasaweb.google.com/data"


def get_user_code_for_device():
    params = {'client_id': client_id, 'scope': scope}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://accounts.google.com/o/oauth2/device/code", data)
    res = urllib2.urlopen(req)
    json_string = res.read()
    json_obj = json.loads(json_string)
    print("got user-dev codes" + json_string)
    return json_obj


def get_tokens_for_user(dev_code):
    params = {'client_id': client_id, 'client_secret': client_secret,
              'grant_type': 'http://oauth.net/grant_type/device/1.0', 'code': dev_code}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://www.googleapis.com/oauth2/v4/token", data)
    res = urllib2.urlopen(req)
    json_string = res.read()
    json_obj = json.loads(json_string)
    print(json_string)
    return json_obj


def get_access_token_using_refresh_token(tok):
    print "Refreshing stale token"
    params = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'refresh_token', 'refresh_token': tok['refresh_token']}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://www.googleapis.com/oauth2/v4/token", data)
    res = urllib2.urlopen(req)
    json_string = res.read()
    json_obj = json.loads(json_string)
    print('token refreshed ' + json_string)
    return json_obj


def make_request(req, tok, data=None, retries=0):
    if retries > 4:
        return ""
    print('Attempting request using ' + tok['access_token'])
    req.add_header('Authorization', 'Bearer ' + tok['access_token'])
    try:
        resp_stream = urllib2.urlopen(req, data)
        res = resp_stream.read()
        print('Response successfully acquired')
        return res
    except urllib2.HTTPError, e:
        print('Error while making request')
        if e.code == 401:
            print('Got a 401. Refreshing tokens')
            tok = get_access_token_using_refresh_token(tok)
            res = make_request(req, tok, None, retries+1)
            return res
        elif e.code == 403:
            print('Got a 403, Refreshing tokens.')
            tok = get_access_token_using_refresh_token(tok)
            res = make_request(req, tok, None, retries+1)
            return res
        elif e.code == 400:
            print('Got a 400. Probably user did not approve permissions')


def get_user_profile_info(tok):
    req = urllib2.Request("https://www.googleapis.com/plus/v1/people/me")
    json_string = make_request(req, tok)
    json_obj = json.loads(json_string)
    name = json_obj['displayName']
    json_obj.tokens = tok
    print name
    return json_obj


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
            id_node = entryNode.getElementsByTagName('gphoto:id')
            title_node = entryNode.getElementsByTagName('title')
            media_group = entryNode.getElementsByTagName('media:group')
            if len(media_group):
                media_group = media_group[0]
                thumbnail = media_group.getElementsByTagName('media:thumbnail')
                thumbnail = thumbnail[0].getAttribute('url')
            if len(id_node):
                album_id = get_text(id_node[0].childNodes)
                title = get_text(title_node[0].childNodes)
                entries.append({'id': album_id, 'title': title, 'thumbnail': thumbnail})
    return entries


def get_user_album_list(tok):
    req = urllib2.Request("https://picasaweb.google.com/data/feed/api/user/default")
    xml_string = make_request(req, tok)
    album_list = parse_xml_for_albums(xml_string)
    return album_list


def parse_xml_for_photos(xmlstr):
    photos = []
    dom = xml.dom.minidom.parseString(xmlstr)
    feed = dom.getElementsByTagName('feed')
    if len(feed) > 0:
        feed = feed[0]
        entry_nodes = feed.getElementsByTagName('entry')
        for entryNode in entry_nodes:
            id_node = entryNode.getElementsByTagName('content')
            title_node = entryNode.getElementsByTagName('title')
            media_group = entryNode.getElementsByTagName('media:group')
            if len(media_group):
                media_group = media_group[0]
                thumbnail = media_group.getElementsByTagName('media:thumbnail')
                thumbnail = thumbnail[0].getAttribute('url')
            if len(id_node):
                url = id_node[0].getAttribute('src')
                title = get_text(title_node[0].childNodes)
                photos.append({'url': url, 'title': title, 'thumbnail': thumbnail})

    return photos


def get_photo_list_for_album(album_id, tokens):
    req = urllib2.Request("https://picasaweb.google.com/data/feed/api/user/default/albumid/" + album_id + '?imgmax=d')
    xml_string = make_request(req, tokens)
    photo_list = parse_xml_for_photos(xml_string)
    print("result returned" + xml_string)
    return photo_list


codes = get_user_code_for_device()
tokens = get_tokens_for_user(codes['device_code'])
info = get_user_profile_info(tokens)
get_access_token_using_refresh_token(info['tokens'])
info = get_user_album_list(info['tokens'])
info = get_photo_list_for_album('', info['tokens'])
