#!/usr/bin/python
import sys, urllib, urllib2, urlparse
import xbmc, xbmcgui
import xbmcplugin
import xml.dom.minidom
import json

base_url = sys.argv[0]

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'pictures')

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)


''' google photos apis '''
client_id = ""
client_secret = ""
scope = "https://picasaweb.google.com/data profile"


def get_user_code_for_device():
    global device_code
    params = {'client_id': client_id, 'scope': scope}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://accounts.google.com/o/oauth2/device/code", data)
    res = urllib2.urlopen(req)
    json_string = res.read()
    json_obj = json.loads(json_string)
    xbmc.log("got user-dev codes" + json_string)
    return json_obj


def get_tokens_for_user(dev_code):
    params = {'client_id': client_id, 'client_secret': client_secret,
              'grant_type': 'http://oauth.net/grant_type/device/1.0', 'code': dev_code}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://www.googleapis.com/oauth2/v4/token", data)
    res = urllib2.urlopen(req)
    json_string = res.read()
    json_obj = json.loads(json_string)
    xbmc.log(json_string)
    return json_obj


def get_access_token_using_refresh_token(tok):
    global access_token
    print "Refreshing stale token"
    params = {'client_id': tok['client_id'], 'client_secret': tok['client_secret'],
              'grant_type': 'refresh_token', 'refresh_token': tok['refresh_token']}
    data = urllib.urlencode(params)
    req = urllib2.Request("https://www.googleapis.com/oauth2/v4/token", data)
    res = urllib2.urlopen(req)
    json_string = res.read()
    json_obj = json.loads(json_string)
    access_token = json_obj['access_token']
    xbmc.log(json_string)
    return json_obj


def make_request(req, tok, data=None):
    xbmc.log('Attempting request')
    req.add_header('Authorization', 'Bearer ' + tok['access_token'])
    try:
        resp_stream = urllib2.urlopen(req, data)
        res = resp_stream.read()
        xbmc.log('Response successfully acquired')
        return res
    except urllib2.HTTPError, e:
        xbmc.log('Error while making request')
        if e.code == 401:
            tok = get_access_token_using_refresh_token(tok)
            res = make_request(req, tok)
            return res
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

''' google photos apis end '''


def build_url(query):
    url = base_url + '?' + urllib.urlencode(query)
    return url


def ShowKeyboard():
    user_input = ''
    exit = True
    while exit:
        kb = xbmc.Keyboard('default', 'heading', True)
        kb.setDefault('')
        kb.setHeading('Authentication')
        kb.setHiddenInput(False)
        kb.doModal()
        if kb.isConfirmed():
            user_input = kb.getText()
            exit = False
    return user_input


if mode is None:
    url = build_url({'mode': 'connect-account'})
    li = xbmcgui.ListItem('Connect a new Google photos account', iconImage='DefaultPicture.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'connect-account':
    # call google api to get device code
    resp = get_user_code_for_device()
    device_code = resp["device_code"]
    user_code = resp["user_code"]
    url = resp["verification_url"]

    heading = "Authenticate"
    line1 = "Step 1. Please visit " + url
    line2 = "Step 2. Enter the code " + user_code
    user_choice = xbmcgui.Dialog().yesno(heading, line1, line2)
    if user_choice:
        xbmc.log("User done auth'ing")
        tokens = get_tokens_for_user(device_code)
        albums = get_user_album_list(tokens)
        for album in albums:
            url = build_url({'mode': 'list-album-photos', 'id': album['id']})
            li = xbmcgui.ListItem(album['title'], iconImage=album['thumbnail'])
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        xbmc.log("User does not want to connect")
