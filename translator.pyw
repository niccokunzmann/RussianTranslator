# -*- coding: utf-8 -*-
################################################################################
##                                                                            ##
##  MIT - License                                                             ##
##  -------------                                                             ##
##                                                                            ##
##  Copyright (c) 2012 Nicco Kunzmann 'niccokunzmann\x40googlemail.com'       ##
##                                                                            ##
##  Permission is hereby granted, free of charge, to any person obtaining     ##
##  a copy of this software and associated documentation files (the           ##
##  "Software"), to deal in the Software without restriction, including       ##
##  without limitation the rights to use, copy, modify, merge, publish,       ##
##  distribute, sublicense, and/or sell copies of the Software, and to        ##
##  permit persons to whom the Software is furnished to do so, subject to     ##
##  the following conditions:                                                 ##
##                                                                            ##
##  The above copyright notice and this permission notice shall be            ##
##  included in all copies or substantial portions of the Software.           ##
##                                                                            ##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,           ##
##  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF        ##
##  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.    ##
##  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY      ##
##  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,      ##
##  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE         ##
##  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                    ##
##                                                                            ##
################################################################################

from Tkinter import *
import urllib
import re
from idlelib.ScrolledList import ScrolledList
import sys
import os
import subprocess
import time
import tempfile
import thread

def allKyrillic(string):
    lower = unichr(1024)
    higher = unichr(1279)
    for letter in string:
        if lower <= letter and letter <= higher:
            # kyrillic letter
            # http://de.wikipedia.org/wiki/Unicodeblock_Kyrillisch
            continue
        if letter == '-':
            continue
        return False
    return True

def lowerKyrillic(string):
    l = []
    # http://de.wikipedia.org/wiki/Unicodeblock_Kyrillisch
    lower = unichr(1040)
    higher = unichr(1071)
    for letter in string:
        if 1040 <= letter <= higher:
            letter = unichr(ord(letter) + 32)
        l.append(letter)
    return type(string)().join(l)

assert lowerKyrillic(u'Произношение') == u'произношение'

root = Tk()
root.title('Translator by Nicco Kunzmann')


def toTop():
##    root.deiconify() ## open if minimized
    root.attributes('-topmost', 1)
    root.attributes('-topmost', 0)

def pollClipboard(last):
    try:
        this = root.clipboard_get().lstrip().rstrip()
    except TclError:
        ## TclError: CLIPBOARD selection doesn't exist or form "STRING" not defined
        this = last
    root.after(20, pollClipboard, this)
    if this != last and allKyrillic(this):
        newWord(this)

def newWord(word):
    import thread
    thread.start_new(play, (word,))
    show(word)

def show(string):
    global f
    urlString = urllib.quote(string.encode('UTF-8'))
    url = 'http://dict.rambler.ru/german-russian/' + urlString
    f = urllib.urlopen(url)
    content = f.read()
    f.close()
    showPage(string, content)
    toTop()

def debug(*args):
    s = ''
    for arg in args:
        try:
            arg = str(arg)
        except:
            arg = repr(arg)
        s += arg + ' '
    sys.stderr.write(s + '\n')

def getTranslations(word, page):
    l = []
    for link, word in translations_re.findall(page):
        link = urllib.unquote(link)
        if link != word:
            debug('getTranslations: %r != %r' % (link, word))
        if word not in l:
            l.append(word)
    return l

translations_re = re.compile('<div class="d-translation">[^<]*<a href='\
                             '"/german-russian/(?P<link>[^"]*)">'\
                             '(?P<translation>[^<]*)</a>')

## http://dict.rambler.ru/german-russian/%D0%BF%D1%80%D0%B8
translations_re_examples = [('''    <div class="d-translation">
        <a href="/german-russian/bei">bei</a>
    </div>
''', ['bei']), ('''<div id="id1" class="d-top-border">
<div class="d-sub-name">
<span class="d-word">увеличение</span>,&nbsp;
	<span class="d-speech">Существительное</span>
	</div><div><div class="d-translation">
	<a href="/german-russian/Vergr%C3%B6%C3%9Ferung">Vergrößerung</a>
	</div></div></div>''', ['Vergrößerung'])]


for example, matches in translations_re_examples:
    found = getTranslations('', example)
    assert found == matches, 'the word %s shall be found in %s' % (matches, found)

def showPage(word, page):
    global page_
    page_ = page
    translations = getTranslations(word, page)
    debug('translated', word, 'into', translations)
    translationList.clear()
    for translation in translations:
        translationList.append(translation)
    root.title(word)

translationList = ScrolledList(root)
root.bind('<Control-c>', lambda event: (root.clipboard_clear(),
                         root.clipboard_append(translationList.get("active"))))

def translateFromEntry(event = None):
    newWord(translationEntry.get())

translationFrame = Frame(root)
translationFrame.pack(side = BOTTOM, fill = X)
translationEntry = Entry(translationFrame)
translationEntry.pack(fill = X, side = LEFT, expand = True)
translationEntry.bind('<KeyPress-Return>', translateFromEntry)
translateButton = Button(translationFrame, command = translateFromEntry, \
                         text = '?')
translateButton.pack(side = RIGHT)

def openAsOpera(url):
    u = urllib.URLopener()
    u.addheaders = []
    u.addheader('User-Agent', 'Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.289 Version/12.01')
    u.addheader('Accept-Language', 'de-DE,de;q=0.9,en;q=0.8')
    u.addheader('Accept', 'text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1')
    f = u.open(url)
    content = f.read()
    f.close()
    return content

oggLinkName = u'Пример произношения'
oggLink_re = re.compile('<a[^>]*href="([^"]*)"[^>]*>Пример произношения</a>')

ogg_re_examples = [('<a href="//upload.wikimedia.org/wikipedia/com'\
                    'mons/d/df/Ru-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D'\
                    '1%80.ogg" class="internal" title="Ru-пример.o'\
                    'gg">Пример произношения</a>', \
                    ['//upload.wikimedia.org/wikipedia/com'\
                    'mons/d/df/Ru-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D'\
                    '1%80.ogg'])]

for example, matches in ogg_re_examples:
    found = oggLink_re.findall(example)
    assert found == matches, 'the word %s shall be found in %s' % (matches, found)


## <a href="//upload.wikimedia.org/wikipedia/commons/d/df/Ru-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80.ogg" class="internal" title="Ru-пример.ogg">Пример произношения</a>

tempnames = []
vlcCommand = ''

def playWithVlc(filename):
    import subprocess
    if not vlcCommand:
        return
    subprocess.Popen([vlcCommand, 'file:///' + filename, '--qt-start-minimized',\
                      '--qt-start-minimized', '--play-and-exit', \
                      '--play-and-stop'], shell = True)


def playOgg(word):
    word = lowerKyrillic(word)
    url = 'http://ru.wiktionary.org/wiki/' + \
              urllib.quote(word.encode('UTF-8'))
    page = openAsOpera(url)
    oggs = oggLink_re.findall(page)
    if oggs:
        ogg = oggs[0]
        if not ogg.startswith('http:'):
            ogg = 'http:' + ogg
        debug('found sound file', ogg)
        import tempfile
        fd, oggfilename = tempfile.mkstemp('.ogg')
        tempnames.append(oggfilename)
        try:
            oggSource = openAsOpera(ogg)
        except IOError:
            return False
        f = file(oggfilename, 'wb')
        f.write(oggSource)
        f.close()
        playWithVlc(oggfilename)
        return True
    return False

play = playOgg

## find path for settings
try: __file__
except:
    __file__ = sys.argv[0]
    i = 0
    while not __file__.lower().endswith('.pyw') and len(sys.argv) > i:
        __file__ = sys.argv[i]
        i+= 1
    if not __file__.lower().endswith('.pyw'):
        __file__ = 'translator.pyw'
        

settingsFile = '.' + os.path.splitext(os.path.basename(__file__))[0] + \
               'settings.dat'

locations = list(map(os.environ.get, ('LOCALAPPDATA', 'APPDATA', 'HOME')))
locations.append('.')
locations = [x for x in locations if x]
settingsPaths = [os.path.join(location, settingsFile) for location in locations]

## load settings

def tryLoad(path):
    global vlcCommand
    if not os.path.isfile(path):
        return False
    try:
        for i, line in enumerate(file(path)):
            line = line[:-1]
            if i == 0:
                geometry = line
            if i == 1:
                vlcCommand = line
    except:
        import traceback
        traceback.print_exc()
        return False
    try:
        root.geometry(geometry)
    except Exception as e:
        import traceback
        traceback.print_exc()
        debug('Exception in tryLoad when setting geometry: %s' % e)
        return False
    return True

def saveSettings(path):
    try:
        f = open(path, 'w')
    except IOError:
        return False
    try:
        ## save geometry
        geometry = root.geometry()
        size = re.match('\\d+x\\d+', geometry).string
        f.write(size + '\n')
        ## save vlcCommand
        f.write(vlcCommand + '\n')
        f.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        debug('Exception in saveSettings: %s' % e)
        return False
    return True

for settingsPath in settingsPaths:
    if tryLoad(settingsPath):
        break
##del settingsPath

def quitRoot(event = None):
    ## save settings
    for settingsPath in settingsPaths:
        if saveSettings(settingsPath):
            break
    root.quit()
    root.destroy()

def searchForVlc(baseDir, cwd = None):
    if cwd is None:
        cwd = tempfile.mkdtemp()
    vlchelp_txt = os.path.join(cwd, 'vlc-help.txt')
    for dirpath, dirnames, filenames in os.walk(baseDir):
        vlcnames = [filename for filename in filenames \
                    if filename.startswith('vlc')]
        if vlcnames:
            debug('could be vlc:', vlcnames, 'in', dirpath)
        vlcnames.sort(key = len) ## shortest first
        for filename in vlcnames:
            _vlcCommand = [os.path.join(dirpath, filename), '--help']
            try:
                p = subprocess.Popen(_vlcCommand, cwd = cwd)
            except OSError:
                continue
            for i in range(500):
                time.sleep(0.001)
                if os.path.exists(vlchelp_txt):
                    ## this must be vlc!
                    return _vlcCommand[0]

if not os.path.exists(vlcCommand):
    vlcCommand = ''
    def findVLC():
        global vlcCommand
        l = [os.environ.get('PROGRAMFILES'), os.environ.get('PROGRAMW6432'), \
             '/usr/bin/', '/bin', '/']
        cwd = tempfile.mkdtemp()
        for searchThere in l:
            if not l:
                continue
            _vlcCommand = searchForVlc(searchThere, cwd = cwd)
            if _vlcCommand:
                vlcCommand = _vlcCommand
                debug('found vlc:', vlcCommand)
                break
    thread.start_new(findVLC, ())


## load settings
root.bind_all("<KeyPress-Escape>", quitRoot)
root.protocol("WM_DELETE_WINDOW", quitRoot)
pollClipboard(u'')
root.mainloop()
for filename in tempnames:
    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except OSError:
            pass
