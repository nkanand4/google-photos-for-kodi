#!/usr/bin/python
import sys, urllib, urllib2, json, urlparse, re
import xbmc, xbmcgui
import xbmcplugin

if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json

import CommonFunctions
common = CommonFunctions
common.plugin = "Google photos"
base_url = sys.argv[0]

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'pictures')

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)


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
    url = build_url({'mode': 'login-as'})
    li = xbmcgui.ListItem('Connect a new Google photos account', iconImage='DefaultPicture.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'login-as':
    string = ShowKeyboard()
