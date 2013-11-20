#!/usr/bin/env python
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
try:
    from idlelib.ScrolledList import ScrolledList
except:
    import sys
    sys.stderr.write('idlelib must be installed\n')
    raise
import sys
import os
import subprocess
import time
import tempfile
import thread
import traceback
import platform
import thread

root = Tk()
root.title('Translator by Nicco Kunzmann')

# ----------------------------- update -----------------------------
## change the following line to higher number to notify other users
## about the new version
__version__ = 6
downloadAndUpdateUrl = 'https://raw.github.com/niccokunzmann/RussianTranslator'\
                       '/master/translator.pyw'
version_re = re.compile('^__version__\s*=\s*(?P<version>\d+)\s*$')
newVersionOfThisFile = None
newVersionNumber = None

def thereIsAnUpdate():
    global newVersionOfThisFile, newVersionNumber
    try:
        content = openAsOpera(downloadAndUpdateUrl)
    except IOError:
        return False
    for line in content.splitlines():
        match = version_re.match(line)
        if match:
            number = int(match.group('version'))
            if number > newVersionShouldBeNewerThan:
                debug('new version available', number, '>', \
                      newVersionShouldBeNewerThan)
                try:
                    compile(content, '<test>', 'exec')
                except:
                    traceback.print_exc()
                    debug('new version', number, 'throws error')
                    return False
                newVersionNumber = number
                newVersionOfThisFile = content
                return True
    return False

searchForUpdates = True ## if you do not want updates: False
askForUpdate = False
newVersionShouldBeNewerThan = __version__

def tryUpdate():
    if searchForUpdates:
        thread.start_new(_tryUpdate, ())

def _tryUpdate():
    global askForUpdate
    if thereIsAnUpdate():
        askForUpdate = True

def installUpdate():
    try:
        lastSource = file(__file__).read()
    except:
        pass
    else:
        try:
            f = file(__file__, 'w')
        except IOError:
            pass
        else:
            try:
                f.write(newVersionOfThisFile)
                f.close()
            except IOError:
                f = file(__file__, 'w')
                f.write(lastSource)
                f.close()
    quitRoot()

def skipUpdate():
    global newVersionShouldBeNewerThan
    assert newVersionNumber is not None
    newVersionShouldBeNewerThan = newVersionNumber
    trySaveSettings()
    quitRoot()

def neverUpdate():
    global searchForUpdates
    searchForUpdates = False
    quitRoot()

def doNothing():
    quitRoot()

installUpdateText = ':) updaten обновлять update'
skipUpdateText =    ':| nicht dieses Update не это обновление' \
                    ' skip this update'
neverUpdateText =   '>:( nie! некогда! never!'
newVersionRoot = Toplevel(root)
newVersionRoot.bind_all("<KeyPress-Escape>", doNothing)
newVersionRoot.protocol("WM_DELETE_WINDOW", doNothing)
newVersionRoot.withdraw()
newVersionRoot.title('updaten обновлять update')
installUpdateButton = Button(newVersionRoot, text = installUpdateText, \
                             command = installUpdate)
installUpdateButton.pack(fill = X)
skipUpdateButton = Button(newVersionRoot, text = skipUpdateText, \
                             command = skipUpdate)
skipUpdateButton.pack(fill = X)
neverUpdateButton = Button(newVersionRoot, text = neverUpdateText, \
                             command = neverUpdate)
neverUpdateButton.pack(fill = X)

hasAskedUpdateQuestion = False

def updateQuestionAsked():
    global hasAskedUpdateQuestion
    if hasAskedUpdateQuestion:
        return True
    hasAskedUpdateQuestion = True
    canUpdate = os.path.exists(__file__)
    if askForUpdate and newVersionOfThisFile and canUpdate:
        newVersionRoot.deiconify()
        root.withdraw()
        return False
    return True

# ----------------------------- kyrillic functions -----------------------------

def allKyrillic(string):
    lower = unichr(1024) ## u'\u0400'
    higher = unichr(1279) ## u'\u04ff'
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
    if isinstance(string, str):
        return lowerKyrillic(string.decode('UTF8')).encode('UTF8')
    assert isinstance(string, unicode)
    return unicodeLowerKyrillic(string)

def unicodeLowerKyrillic(string):
    l = []
    # http://de.wikipedia.org/wiki/Unicodeblock_Kyrillisch
    lower = unichr(1040)
    higher = unichr(1071)
    for letter in string:
        if lower <= letter <= higher:
            letter = unichr(ord(letter) + 32)
        l.append(letter)
    return type(string)().join(l)

assert lowerKyrillic(u'Произношение') == u'произношение'
assert lowerKyrillic('Произношение') == 'произношение'

# ----------------------------- stack -----------------------------

translationFrame = Frame(root)


_translationStack = []

def push_translation(translation):
    assert translation is not None
    _translationStack.append(translation)
    root.after(10, updateToLastTranslationButton)

def last_translation():
    if len(_translationStack) < 2:
        return None
    return _translationStack[-2]

def pop_translation():
    t = last_translation()
    if _translationStack:
        _translationStack.pop(-1)
    root.after(10, updateToLastTranslationButton)
    return t

def updateToLastTranslationButton():
    if last_translation() is None:
        toLastTranslationButton.pack_forget()
    else:
        toLastTranslationButton['text'] = last_translation()
        toLastTranslationButton.pack()

def goToLastWord(event = None):
    last_translation = pop_translation()
    if last_translation:
        translateWord(last_translation)

toLastTranslationButton = Button(translationFrame, command = goToLastWord)
toLastTranslationButton.pack(side = RIGHT)
updateToLastTranslationButton()

# ----------------------------- translation -----------------------------


def toTop():
##    root.deiconify() ## open if minimized
    root.attributes('-topmost', 1)
    root.attributes('-topmost', 0)

def pollClipboard(last):
    try:
        this = root.clipboard_get()
    except TclError as e:
        ## TclError: CLIPBOARD selection doesn't exist or form "STRING" not defined
        this = last

    root.after(20, pollClipboard, this)
    if this != last:
        this = toRussian(this)
        if allKyrillic(this):
            newWord(this)

isUnicode_re = re.compile('^(?:\\\\u[0123456789abcdef]{4})*$')

assert isUnicode_re.match('\\u0435\\u0449\\u0451') is not None
assert isUnicode_re.match('\\u0435\\u0449\\u0451').string == '\\u0435\\u0449\\u0451'
assert isUnicode_re.match('asdf') is None
assert isUnicode_re.match('\\u0435\\u0449aa\\u0451') is None

def toRussian(word):
    word = word.lstrip().rstrip()
    ## sometimes word look like unicode strings under linux
    ## \u0435\u0449\u0451 = ещё
    if isUnicode_re.match(word):
        word = eval('u"%s"' % word)
    return word

def newWord(word):
    push_translation(word)
    translateWord(word)

def translateWord(word):
    global threadThatCanPlay
    ## todo: use thread id for playing only last wanted word
    assert isinstance(word, basestring)
    thread.start_new(play, (word,))
    show(word)

def show(string):
    global f
    urlString = urllib.quote(string.encode('UTF-8'))
    url = 'http://de.pons.eu/dict/search/results/?q=%s&l=deru&in=&lf=de' % urlString
    f = urllib.urlopen(url)
    content = f.read()
    f.close()
    if f.code == 200:
        showPage(string, content)
    else:
        fillTranslationList(u'Fehler, ошипка, error %s' % f.code, \
                            ['de.pons.eu geht nicht', \
                             'de.pons.eu не работает', \
                             'de.pons.eu stopped working', \
                             url])
    toTop()

def debug(*args):
    s = ''
    for arg in args:
        try:
            ## use debug because command line print may fail for unicode
            arg = str(arg)
        except:
            arg = repr(arg)
        s += arg + ' '
    sys.stderr.write(s + '\n')

def getPossibleEncodings(word):
    words = []
    try:
        words.append(word.encode('UTF8'))
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    try:
        words.append(word.decode('UTF8'))
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    if word not in words:
        words.append(word)
    return words

def removeAccentuation(word):
    assert type(word) is str
    return word.replace('́', '')

def getTranslations(word, page):
    words = list(map(removeHTML, getPossibleEncodings(word)))
    exactMatches = []
    matches = []
    for match in translations_re.finditer(page):
        searched, result = match.group('searched', 'result')
        searched, result = getEntry(searched), getEntry(result)
        if removeAccentuation(searched) in words or searched in words:
            exactMatches.append(result)
        else:
            if not searched in matches:
                matches.append(searched)
            matches.append(result)
    return exactMatches + matches

def getEntry(match):
    spans = []
    def replaceSpan(span):
        result = span.group('span') or span.group('sense')
        spans.append(removeHTML(result))
        return ''
    result = removeHTML(span_re.sub(replaceSpan, match))
    if spans:
        result += ' [%s]' % ', '.join(spans)
    return result

def removeAnnotation(string):
    if '[' in string:
        return string[:string.rfind('[')]
    return string
    
span_re = re.compile('<span\\s+class="sense">\\(?(?P<sense>[^<]*?)\\)?</span>|'\
                     '<span(?!\\s+class="idiom_proverb")[^>]*>(?P<span>.*?)</span>'\
                     , re.DOTALL)

def removeHTML(string):
    s = removeHTML_re.sub('', string)
    s = whitespace_re.sub(' ', s)
    if not s:
        return s
    return s[s[0] == ' ':len(s) - (s[-1] == ' ')]

removeHTML_re = re.compile('<[^>]*>')
whitespace_re = re.compile('\\s+')
translations_re = re.compile('<(?P<open1>td|div)\s+class="source"\s*>(?P<searched>.*?)</(?P=open1)>.*?'\
                             '<(?P<open2>td|div)\s+class="target"\s*>(?P<result>.*?)</(?P=open2)>', re.DOTALL)
# from word , source, to word
translations_re_examples = [('при', ''' 
    </td>
    <td class="source" >
      <span class="idiom_proverb"><strong class="tilde">
				при</strong> э́том</span>
    </td>
      <td class="target">
        dabei
      </td>
    <td class="options right">
      ''', ['при э́том', 'dabei']), ('увеличение', '''    <td class="source">
      <strong class="headword">увеличе́ние</strong>
    </td>
      <td class="target">
        <a href="/deutsch-russisch/Vergr%C3%B6%C3%9Ferung">Vergrößerung</a> <span class="genus"><acronym title="Femininum">f</acronym></span>
      </td>''', ['Vergrößerung [f]']),
('очевидно', ''' <td class="source"><strong class="headword">очеви́дно</strong>
    </td>
    
      <td class="target">
        <a href="/deutsch-russisch/offensichtlich">offensichtlich</a>
      </td>
    
    <td class="options right">
      
        <ul>
          
            <li>  
              <a href="/open_dict/audio_tts/de/Tderu7793532?l=deru" class="tts play_btn trackable trk-audio ">
                <span class="icon audio">
                  
                </span>
              </a>
            </li>
          
            <li>
              <span class="icon circle-plus trainerAddSingle" title="Diese Übersetzung in den PONS Vokabeltrainer übernehmen"></span>
            </li>
          
        </ul>
      
      <div class="acapela">
        powered by <a href="http://www.acapela-group.com" target="_blank">acapela</a> text to speech
      </div> 
    </td>
  
</tr>



<tr id="Tderu7793533" class="kne" data-translation="1">
  
    <td class="options left"> 
      <ul>
        
          <li>
            <span class="icon circle-plus trainerAddSingle" title="Diese Übersetzung in den PONS Vokabeltrainer übernehmen"></span>
          </li>
        
          <li>  
          	
              <a href="/open_dict/audio_tts/ru/Tderu7793533?l=deru" class="tts play_btn trackable trk-audio ">
                <span class="icon audio">
                  
                </span>
              </a>
            
          </li>
        
      </ul>
      <div class="acapela">
        powered by <a href="http://www.acapela-group.com" target="_blank">acapela</a> text to speech
      </div> 
    </td>
    <td class="source">
      <strong class="headword">очеви́дно</strong>
    </td>
    
      <td class="target">
        <a href="/deutsch-russisch/offenkundig">offenkundig</a>
        </td>''', \
                            ['offensichtlich', 'offenkundig']),
    ('при', '\xef\xbb\xbf<div class="translations first opened">\n\n          <h3 class="empty hidden">\n            \n          </h3>\n\n          \n\n<dl id="Tderu7823426" class="dl-horizontal kne first" data-translation="0">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <strong class="headword"><a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/bei">bei</a> <span class="object-case">+<acronym title="Dativ">dat</acronym></span>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823427" class="dl-horizontal kne" data-translation="1">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb">\xd1\x8f <a href="/russisch-deutsch/%D1%82%D1%83%D1%82">\xd1\x82\xd1\x83\xd1\x82</a> <a href="/russisch-deutsch/%D0%BD%D0%B8">\xd0\xbd\xd0\xb8</a> <strong class="tilde"><a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D1%87%D1%91%D0%BC">\xd1\x87\xd1\x91\xd0\xbc</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/ich">ich</a> <a href="/deutsch-russisch/habe">habe</a> <a href="/deutsch-russisch/damit">damit</a> <a href="/deutsch-russisch/nichts">nichts</a> <a href="/deutsch-russisch/zu">zu</a> <a href="/deutsch-russisch/tun">tun</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823428" class="dl-horizontal kne" data-translation="2">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb"><strong class="tilde">\n\t\t\t\t<a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D1%8D%CC%81%D1%82%D0%BE%D0%BC">\xd1\x8d\xcc\x81\xd1\x82\xd0\xbe\xd0\xbc</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/dabei">dabei</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823429" class="dl-horizontal kne" data-translation="3">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb"><strong class="tilde">\n\t\t\t\t<a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D1%8D%CC%81%D1%82%D0%BE%D0%BC">\xd1\x8d\xcc\x81\xd1\x82\xd0\xbe\xd0\xbc</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/hierbei">hierbei</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823430" class="dl-horizontal kne" data-translation="4">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb"><strong class="tilde">\n\t\t\t\t<a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D0%B2%D1%81%D0%B5%D1%85">\xd0\xb2\xd1\x81\xd0\xb5\xd1\x85</a> <a href="/russisch-deutsch/%D1%82%D1%80%D1%83%CC%81%D0%B4%D0%BD%D0%BE%D1%81%D1%82%D1%8F%D1%85">\xd1\x82\xd1\x80\xd1\x83\xcc\x81\xd0\xb4\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x8f\xd1\x85</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/trotz">trotz</a> <a href="/deutsch-russisch/aller">aller</a> <a href="/deutsch-russisch/Schwierigkeiten">Schwierigkeiten</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823431" class="dl-horizontal kne" data-translation="5">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb"><strong class="tilde">\n\t\t\t\t<a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D0%BA%D0%B0%D0%BF%D0%B8%D1%82%D0%B0%D0%BB%D0%B8%CC%81%D0%B7%D0%BC%D0%B5">\xd0\xba\xd0\xb0\xd0\xbf\xd0\xb8\xd1\x82\xd0\xb0\xd0\xbb\xd0\xb8\xcc\x81\xd0\xb7\xd0\xbc\xd0\xb5</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/im">im</a> <a href="/deutsch-russisch/Kapitalismus">Kapitalismus</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823432" class="dl-horizontal kne" data-translation="6">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb"><strong class="tilde">\n\t\t\t\t<a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D1%82%D0%B5%D0%BF%D0%B5%CC%81%D1%80%D0%B5%D1%88%D0%BD%D0%B5%D0%BC">\xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xcc\x81\xd1\x80\xd0\xb5\xd1\x88\xd0\xbd\xd0\xb5\xd0\xbc</a> <a href="/russisch-deutsch/%D1%83%CC%81%D1%80%D0%BE%D0%B2%D0%BD%D0%B5">\xd1\x83\xcc\x81\xd1\x80\xd0\xbe\xd0\xb2\xd0\xbd\xd0\xb5</a> <a href="/russisch-deutsch/%D0%B7%D0%BD%D0%B0%CC%81%D0%BD%D0%B8%D0%B9">\xd0\xb7\xd0\xbd\xd0\xb0\xcc\x81\xd0\xbd\xd0\xb8\xd0\xb9</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/nach">nach</a> <a href="/deutsch-russisch/dem">dem</a>  <span class="target">[<span class="or"><a href="/deutsch-russisch/%D0%B8%D0%BB%D0%B8">\xd0\xb8\xd0\xbb\xd0\xb8</a></span> <a href="/deutsch-russisch/beim">beim</a>]</span>  <a href="/deutsch-russisch/heutigen">heutigen</a> <a href="/deutsch-russisch/Wissensstand">Wissensstand</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n<dl id="Tderu7823433" class="dl-horizontal kne" data-translation="7">\n  \n\n    <dt> \n      <div class="dt-inner">  \n        <ul class="inline translation-options">\n          \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="ru">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n        </ul>\n\n        <div class="source">\n        <span class="idiom_proverb"><a href="/russisch-deutsch/%D0%B8%D0%BC%D0%B5%CC%81%D1%82%D1%8C">\xd0\xb8\xd0\xbc\xd0\xb5\xcc\x81\xd1\x82\xd1\x8c</a> <strong class="tilde"><a href="/russisch-deutsch/%D0%BF%D1%80%D0%B8">\xd0\xbf\xd1\x80\xd0\xb8</a></strong> <a href="/russisch-deutsch/%D1%81%D0%B5%D0%B1%D0%B5%CC%81">\xd1\x81\xd0\xb5\xd0\xb1\xd0\xb5\xcc\x81</a></span>\n        </div>\n      </div>\n    </dt> \n\n    \n\n      <dd> \n        <div class="dd-inner"> \n          <div class="target">  \n          <a href="/deutsch-russisch/bei">bei</a> <a href="/deutsch-russisch/sich">sich</a> <a href="/deutsch-russisch/haben">haben</a>\n          </div> \n\n          <ul class="inline translation-options">\n\n            \n\n  <li>\n    <a href="#" class="audio tts trackable trk-audio " data-pons-lang="de">\n      <i class="icon-volume-down"></i> \n    </a>\n  </li>\n\n\n              <li class="dropdown">\n                <a href="#" data-toggle="dropdown">\n                  <i class="icon-plus-sign"></i> \n                </a>\n                <ul class="dropdown-menu">\n                  <li>\n                    <a class="favorites" href="#">\n                      <i class="icon-star"></i> \n                      &nbsp;Zu meinen Favoriten hinzuf\xc3\xbcgen\n                    </a>\n                  </li>\n                  <li>\n                    <a class="trainer" href="#">\n                      <i class="icon-inbox"></i> \n                      &nbsp;F\xc3\xbcr den Vokabeltrainer vormerken\n                    </a> \n                  </li>\n                  <li>\n                    <a class="trainer-import" href="/trainer-import">\n                      <i class="icon-inbox"></i> \n                      &nbsp;Vorgemerkte Vokabeln ansehen\n                    </a> \n                  </li>\n                  \n                </ul>\n              </li>\n            \n          </ul>\n        </div>  \n      </dd>\n    \n\n</dl>\n\n\n\n        </div>',
     ['bei [+dat]', '\xd1\x8f \xd1\x82\xd1\x83\xd1\x82 \xd0\xbd\xd0\xb8 \xd0\xbf\xd1\x80\xd0\xb8 \xd1\x87\xd1\x91\xd0\xbc', 'ich habe damit nichts zu tun', '\xd0\xbf\xd1\x80\xd0\xb8 \xd1\x8d\xcc\x81\xd1\x82\xd0\xbe\xd0\xbc', 'dabei', 'hierbei', '\xd0\xbf\xd1\x80\xd0\xb8 \xd0\xb2\xd1\x81\xd0\xb5\xd1\x85 \xd1\x82\xd1\x80\xd1\x83\xcc\x81\xd0\xb4\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x8f\xd1\x85', 'trotz aller Schwierigkeiten', '\xd0\xbf\xd1\x80\xd0\xb8 \xd0\xba\xd0\xb0\xd0\xbf\xd0\xb8\xd1\x82\xd0\xb0\xd0\xbb\xd0\xb8\xcc\x81\xd0\xb7\xd0\xbc\xd0\xb5', 'im Kapitalismus', '\xd0\xbf\xd1\x80\xd0\xb8 \xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xcc\x81\xd1\x80\xd0\xb5\xd1\x88\xd0\xbd\xd0\xb5\xd0\xbc \xd1\x83\xcc\x81\xd1\x80\xd0\xbe\xd0\xb2\xd0\xbd\xd0\xb5 \xd0\xb7\xd0\xbd\xd0\xb0\xcc\x81\xd0\xbd\xd0\xb8\xd0\xb9', 'nach dem beim] heutigen Wissensstand [[\xd0\xb8\xd0\xbb\xd0\xb8]', '\xd0\xb8\xd0\xbc\xd0\xb5\xcc\x81\xd1\x82\xd1\x8c \xd0\xbf\xd1\x80\xd0\xb8 \xd1\x81\xd0\xb5\xd0\xb1\xd0\xb5\xcc\x81', 'bei sich haben']),
    ]


for word, page, matches in translations_re_examples:
    found = getTranslations(word, page)
    assert found == matches, ' %s \n  ==  \n %s' % (matches, found)

def showPage(word, page):
    global page_
    page_ = page
    translations = getTranslations(word, page)
    debug('translated', word, 'into', translations)
    fillTranslationList(word, translations)

def fillTranslationList(word, translations):
    translationList.clear()
    for translation in translations:
        translationList.append(translation)
    if not translations:
        translationList.append('')
    root.title(word)

def getListWord(index = 'active'):
    return removeAnnotation(translationList.get(index))

def on_double_click(index):
    newWord(getListWord())

def copyFromList(event = None):
    root.clipboard_clear()
    wordToCopy = getListWord()
    
    root.clipboard_append(wordToCopy)

translationList = ScrolledList(root)
translationList.listbox['height'] = 3
translationList.on_double = on_double_click
translationList.append('')
translationList.listbox.bind('<Control-c>', copyFromList)

def translateFromEntry(event = None):
    newWord(translationEntry.get())

translationFrame.pack(side = BOTTOM, fill = X)
translationEntry = Entry(translationFrame, width = 5)
translationEntry.pack(fill = X, side = LEFT, expand = True)
translationEntry.bind('<KeyPress-Return>', translateFromEntry)


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
    command = [vlcCommand, 'file:///' + filename, '--qt-start-minimized',\
               '--qt-start-minimized', '--play-and-exit', '--play-and-stop']
    debug('running vlc:', *command)
    p = subprocess.Popen(command, \
                        stdin = subprocess.PIPE, \
                        stdout = subprocess.PIPE, \
                        stderr = subprocess.PIPE)

def playWithMplayer(filename):
    subprocess.call(('mplayer', filename))

downloadedOggFiles = {} ## word : oggfilename

def getOggFile(word):
    word = lowerKyrillic(word)
    if word in downloadedOggFiles:
        oggfilename = downloadedOggFiles[word]
        if os.path.isfile(oggfilename):
            return oggfilename
        del oggfilename
    url = 'http://ru.wiktionary.org/wiki/' + \
              urllib.quote(word.encode('UTF-8'))
    try:
        debug('looking for', word, 'at', url)
        page = openAsOpera(url)
    except IOError:
        return False
    oggs = oggLink_re.findall(page)
    if oggs:
        ogg = oggs[0]
        if not ogg.startswith('http:'):
            ogg = 'http:' + ogg
        debug('found sound file', ogg)
        fd, oggfilename = tempfile.mkstemp('.ogg')
        os.close(fd)
        tempnames.append(oggfilename)
        try:
            oggSource = openAsOpera(ogg)
        except IOError:
            debug('sound file could not be opened:', ogg)
            return False
        f = file(oggfilename, 'wb')
        try: f.write(oggSource)
        finally: f.close()
        downloadedOggFiles[word] = oggfilename
        return oggfilename
    return None


threadThatCanPlay = None

def playOgg(word):
    oggfilename = getOggFile(word)
    if oggfilename and threadThatCanPlay == thread.get_ident():
        if hasVLC:
            playWithVlc(oggfilename)
        elif hasMplayer:
            playWithMplayer(oggfilename)
        return True
    return False

def play(word):
    global threadThatCanPlay
    threadThatCanPlay = thread.get_ident()
    playOgg(word)

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
    global vlcCommand, searchForUpdates, newVersionShouldBeNewerThan
    global hasVLC
    if not os.path.isfile(path):
        return False
    gmometry = None
    try:
        for i, line in enumerate(file(path)):
            line = line[:-1]
            if i == 0:
                geometry = line
            if i == 1:
                vlcCommand = line
                if os.path.exists(vlcCommand):
                    hasVLC = True
            if i == 2:
                searchForUpdates = not line.lower().startswith('no updates')
            if i == 3 and line.isdigit():
                newValue = int(line)
                if newValue > newVersionShouldBeNewerThan:
                    newVersionShouldBeNewerThan = newValue
    except:
        import traceback
        traceback.print_exc()
        return False
    else:
        if geometry is None:
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
        size = re.match('(\\d+x\\d+)', geometry).group()
        f.write(size + '\n')
        ## save vlcCommand
        f.write(vlcCommand + '\n')
        f.write(('search for updates' if searchForUpdates else 'no updates') + '\n')
        f.write(str(newVersionShouldBeNewerThan) + '\n')
        f.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        debug('Exception in saveSettings: %s' % e)
        return False
    return True

hasVLC = False

for settingsPath in settingsPaths:
    if tryLoad(settingsPath):
        break
##del settingsPath

def trySaveSettings():
    for settingsPath in settingsPaths:
        if saveSettings(settingsPath):
            break

def quitRoot(event = None):
    ## save settings
    if updateQuestionAsked():
        trySaveSettings()
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
                p = subprocess.Popen(_vlcCommand, cwd = cwd,
                                     stdin = subprocess.PIPE, \
                                     stdout = subprocess.PIPE, \
                                     stderr = subprocess.PIPE)
            except OSError:
                continue
            stdout = ''
            for i in range(500):
                time.sleep(0.001)
                stdout += p.stdout.read()
                if os.path.exists(vlchelp_txt):
                    ## windows7 vlc 2.xx
                    return _vlcCommand[0]
                if ('vlc' in stdout or 'VLC' in stdout) \
                   and '--play-and-stop' in stdout \
                   and '--play-and-exit' in stdout:
                    ## ubuntu vlc 1.xx
                    return _vlcCommand[0]


if platform.system() == 'Darwin':
    # Mac OS may have Mplayer
    hasMplayer = subprocess.call(('hash', 'mplayer')) == 0
else:
    hasMplayer = False

if not os.path.exists(vlcCommand) and not hasMplayer and not hasVLC:
    vlcCommand = ''
    def findVLC():
        global vlcCommand, hasVLC
        l = [os.environ.get('PROGRAMFILES'), os.environ.get('PROGRAMW6432'), \
             '/usr/bin/', '/bin', '/']
        cwd = tempfile.mkdtemp()
        for searchThere in l:
            if not searchThere:
                continue
            _vlcCommand = searchForVlc(searchThere, cwd = cwd)
            if _vlcCommand:
                vlcCommand = _vlcCommand
                hasVLC = True
                debug('found vlc:', vlcCommand)
                break
    thread.start_new(findVLC, ())


## settings loaded
tryUpdate()
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

