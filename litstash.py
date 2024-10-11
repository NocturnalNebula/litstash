#!/usr/bin/env python3

#    LICENSE INFORMATION: GNU GPLv3.0-or-later

#    litstash is a downloader of submissions from Literotica and xnxx stories

#    Copyright (C) 2023 NocturnalNebula <nocturnalnebula@tutamail.com>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#    < --- PROGRAM BEGINS BELOW --- >

# This is a long script and is best read in an IDE with all functions collapsed/folded.

# import modules (all from standard library)
import urllib.request
import urllib.error
import os
import sys
import time
import json
import traceback

# initialize global variables
origCwd = os.getcwd()
downloadList = []
version = 'Version: 1.8'
updated = 'Updated: July 2024'
usage = '''
litstash is a story downloader with support for the sites Literotica and xnxx,
including Wayback Machine captures of either site

usage:
    litstash [option]
    litstash ["URL"...]

    OR (if running script with Python)

    python litstash.py [option]
    python litstash.py ["URL"...]

options:
    -h, --help    print usage guide
    --version     print version number
    -a            automatically download all detected submissions

URL:
    - URLs should be surrounded by "quotes" to prevent an '&' from confusing the shell
    - URLs are any of the following:
        - Literotica submission (story, poem, audio, illustration)
        - xnxx story (sexstories.com)
        - any page containing links to either of the above
        - Series Pages (for batch downloading a series)
        - Author Pages (for batch downloading all of an author's works)
        - Wayback Machine capture of any of the above
    - multiple URLs can be included

examples:
    python litstash.py --version
    python litstash.py https://www.literotica.com/s/an-erotic-story-9 https://www.literotica.com/p/a-smutty-poem-8
    python litstash.py https://www.literotica.com/series/se/00000
    python litstash.py https://www.literotica.com/authors/a-literotica-author
    python litstash.py "https://web.archive.org/web/20130919123456/https://www.literotica.com/s/a-deleted-story-4"
    python litstash.py -a "https://web.archive.org/web/20130723123456/https://www.literotica.com/stories/memberpage.php?uid=0000000&page=submissions"

more:
    - downloads will be saved in 'litstash-saves' created in the current working directory
    - visit https://github.com/NocturnalNebula/litstash/releases to check for new versions
    
contact:
    - created in Jan 2023 by NocturnalNebula
    - email: nocturnalnebula@tutamail.com
'''

# CLASSES

class literotica:

    def __init__(self, url):
        # immediately defined
        self.url = url
        self.slug = self.url.split('/')[-1]
        self.publisher = "Literotica"

        self.apiData = {} # dict from rest api
        self.pageSource = ''

        # submission metadata
        self.title = ''
        self.username = ''
        self.series = ''
        self.date = ''
        self.description = ''
        self.category = ''
        self.pages = 1 # total pages in submission, default=1, change later

        # submission text attributes
        self.text = ''
        self.currentPage = 1
        self.wordCount = ''

        self.skip = 0 # skipping flag if there is a problem getting page source
        # build items
        self.output = ''
        self.path = ''
        self.filename = ''

    def getApiData(self):
        # collect data from api, put into a dict

        url = 'https://literotica.com/api/3/stories/'+self.slug+'?params={"contentPage":'+str(self.currentPage)+'}'
        source = getSource(url)

        if source == 'skip': self.skip = 1; return

        self.apiData = json.loads(source)

        # submission should be skipped if they don't have page text, unless they are illustrations
        if not 'pageText' in self.apiData:
            if self.apiData['submission']['category_info']['pageUrl'] in ['adult-comics','erotic-art']:
                return
            print('No submission text. Skipping...')
            self.skip = 1

    # PRIMARY METHODS
    def download(self):
    # collect all data needed to export the submission

        print(f"\n[Downloading] {cleanTitle(self.url)} ({getSite(self.url)})")
        print(f"[URL]         {self.url}")

        # loop through each page of the story, scraping the text of each page
        while self.currentPage <= self.pages:

            self.getApiData()

            if self.skip == 1: return

            # get metadata on first loop
            if self.currentPage == 1:

                self.pages = self.apiData['meta']['pages_count']
                if self.pages is None: self.pages = 1

                # rearrange date into year/month/day format
                date = self.apiData['submission']['date_approve'].split('/')
                self.date = ('-').join([date[2],date[0],date[1]])

                # ensure title is a string (default will be int if only digits)
                self.title = str(self.apiData['submission']['title']).replace('/','-')

                self.username = str(self.apiData['submission']['authorname'])
                self.description = str(self.apiData['submission']['description'])
                self.category = getCategory(self.apiData['submission']['category_info']['pageUrl'])

                # get series data only if it exists
                try:
                    self.series = self.apiData['submission']['series']['meta']['title']
                except TypeError:
                    pass
                    
            # need to get real page source for illusration categories
            if self.category == 'Adult Comics' or self.category == 'Erotic Art':
                # get page source to gather pageText, send it into getImages
                url = self.url + '?page=' + str(self.currentPage)
                self.pageSource = getSource(url)
                pageText = cleanIllustrationSource(self)
            elif self.apiData['pageText'] is not None:
                pageText = self.apiData['pageText']
                pageText = pageText.replace('\r\n\r\n','</p>\n<p>')
                pageText = pageText.replace('\r\n','<br>\n')
            else:
                pageText = ''

            # if category = Audio, search page for audio links and append to pageText
            if self.category == 'Audio' or self.category == 'Poetry With Audio':
                url = self.url + '?page=' + str(self.currentPage)
                pageText = getAudio(pageText, getSource(url), self.title, self.username)

            # append current page text to master text string
            self.text += f"<p>{pageText}</p>"

            print(f"[Saved]       Page {self.currentPage} of {self.pages}")
            self.currentPage += 1

        self.wordCount = wordCount(self.text)

        # scan finished master text string for <img> tags and to download any images (for illustrated stories)
        self.text = getImages(self.text, self.username)

    def build(self):
    # prepare all retrieved submission data for export

        self.output = getOutput(self)
        self.path = getPath(self.username)
        self.filename = getFilename(self.date,self.title)

    def export(self):
        export(self.path, self.filename, self.output)

class waybackMachineLit:

    def __init__(self, url):
        # immediately defined
        self.url = url
        self.slug = self.url.split('/')[-1]
        self.authorPageUrl = ''
        self.publisher = "Literotica"


        self.pageSource = ''

        # submission metadata (filled with first page)
        self.scheme = '' # Modern / Classic / Pre-Classic / Original
        self.title = ''
        self.username = ''
        self.series = ''
        self.date = ''
        self.description = ''
        self.category = ''
        self.pages = 1 # total pages in submission (default = 1, change later)

        # submission text attributes
        self.text = ''
        self.pageText = ''
        self.currentPage = 1
        self.wordCount = ''

        self.skip = 0 # skipping flag if there is a problem getting page source
        # build items
        self.output = ''
        self.path = ''
        self.filename = ''

    # HELPER METHODS
    def getDateFromAuthor(self):
    # for submissions without an upload date, retrieve it from the author page

        if self.authorPageUrl == '':
            print('Cannot find author page URL.')
            print('Try a different Wayback Machine capture to include the upload date.')
            self.date = '0000-00-00'
            return

        if self.authorPageUrl.startswith('//'):
            self.authorPageUrl = 'https:'+ self.authorPageUrl

        authorPageSource = getSource(self.authorPageUrl.replace('&amp;','&'))

        # some author pages won't be captured by wayback machine
        if '<b>This member does not exists</b>' in authorPageSource:
            print('No capture available of author page.')
            print('Try a different Wayback Machine capture to include the upload date.')
            self.date = '0000-00-00'
            return
        else:
            # put the index before the relevant entry
            i = authorPageSource.find(f'/{self.slug}')
            if i == -1:
                print('Cannot find submission upload date on author page.')
                print('Try a different Wayback Machine capture to include the upload date.')
                self.date = '0000-00-00'
                return

            # scan forward from submission url to a substring mataching the date format (>**/**/**) *=digit
            date = ''
            while len(date) < 9:

                if authorPageSource[i] in '0123456789/>': date += authorPageSource[i]
                else: date = ''
                if len(date) > 0 and date.count('>') != 1: date = ''
                i += 1

            # create date format year/month/date
            date = date[1:].split('/')
            self.date = ('-').join(['20'+date[2],date[0],date[1]])

    def getPageSource(self, url='', attempts=0):

        if attempts == 3:
            print('Wayback Machine capture is unavailable.')
            self.skip = 1
            return

        if url != '':
            source = getSource(url)

        else:
            # older captures (pre ~2010) have different url formats
            if self.scheme == 'Original' or self.scheme == 'Post-Original':
                pageSlug = f"&page={self.currentPage}"
            else: pageSlug = f"?page={self.currentPage}"

            if self.currentPage == 1: pageSlug = ''

            source = getSource(self.url + pageSlug)

        self.pageSource = source

        if '>Got an HTTP 301 response at crawl time<' in self.pageSource:
            print('Got an HTTP Error 301 from Wayback Machine. Redirecting...')
            attempts += 1
            self.getPageSource(sandwichMaker(self.pageSource,'class="impatient"><a href="','"'),attempts)

        if '>Got an HTTP 302 response at crawl time<' in self.pageSource:
            print('Got an HTTP Error 302 from Wayback Machine. Redirecting...')
            attempts += 1
            self.getPageSource(sandwichMaker(self.pageSource,'class="impatient"><a href="','"'),attempts)

        if self.pageSource == 'skip':
            self.skip = 1
            return

    def getScheme(self):
    # determine lit site scheme of wayback capture

        if self.pageSource == '':
            print('Error: No page source was loaded')
            self.skip = 1
            return

        # each scheme has subtle differences in html layout, but relevant to data extraction
        if 'class="aa_ht"' in self.pageSource: self.scheme = 'Modern'
        elif 'class="b-story-body-x x-r15"' in self.pageSource: self.scheme = 'Classic'
        elif 'class="b-story-body"' in self.pageSource: self.scheme = 'Pre-Classic'
        elif '<font size="2">' in self.pageSource: self.scheme = 'Original'
        elif '<div id="content"><p>' in self.pageSource: self.scheme = 'Post-Original'
        else:
            print('Error: Unable to retrieve submission from this Wayback Machine capture.')
            print('Try a different capture of the same submission.')
            self.skip = 1
            return

    def downloadModern(self):

        # get metadata on first loop (find all data in the page source)
        if self.currentPage == 1:

            self.title = sandwichMaker(self.pageSource, '<h1 class="j_bm headline j_eQ">', '<')
            self.title = self.title.replace('&quot;','"').replace('&#x27;',"'").replace('&amp;','&').replace('/','-')

            if '/s/' in self.url:
                if self.pageSource.count(f"literotica.com/s/{self.slug}?page=") > 0:
                    self.pages = int(sandwichMaker(self.pageSource, f"literotica.com/s/{self.slug}?page=", '"', reverse=1))

            if '/p/' in self.url:
                if self.pageSource.count(f"literotica.com/p/{self.slug}?page=") > 0:
                    self.pages = int(sandwichMaker(self.pageSource, f"literotica.com/p/{self.slug}?page=", '"', reverse=1))

            if '/i/' in self.url:
                if self.pageSource.count(f"literotica.com/i/{self.slug}?page=") > 0:
                    self.pages = int(sandwichMaker(self.pageSource, f"literotica.com/i/{self.slug}?page=", '"', reverse=1))

            self.username = sandwichMaker(self.pageSource, 'class="y_eR" title="', '">')
            self.description = sandwichMaker(self.pageSource, 'name="description" content="', '">')

            # put date in year/month/day format
            date = sandwichMaker(self.pageSource, '"date_approve":"', '"').split('/')
            self.date = ('-').join([date[2],date[0],date[1]])

            self.wordCount = sandwichMaker(self.pageSource, '"words_count":', ',')
            self.category = getCategory(sandwichMaker(self.pageSource, '/https://www.literotica.com/c/', '"'))

            print('[Retrieved]   Submission Metadata')


        # extract and clean up pageText from pageSource
        # illustration categories have <img> tags below normal page text
        if self.category == 'Adult Comics' or self.category == 'Erotic Art':
            self.pageText = sandwichMaker(self.pageSource,'<div class="aa_ht">','<div class="aa_hv aa_hy">')
        else:
            self.pageText = self.pageSource.split('<div class="aa_ht">')
            self.pageText = self.pageText[1].replace('<div>','').replace('</div>','')

    def downloadClassic(self):
        # get metadata on first loop
        if self.currentPage == 1:

            title = sandwichMaker(self.pageSource,'<h1>','</h1>')
            self.title = title.replace('&quot;','"').replace('&#x27;',"'").replace('&amp;','&').replace('/','-')

            self.pages = int(sandwichMaker(self.pageSource,'<!-- x -->',' Pages'))
            self.username = sandwichMaker(self.pageSource,'page=submissions">','</a>')
            self.description = sandwichMaker(self.pageSource,'name="description" content="','"')
            self.category = getCategory(sandwichMaker(self.pageSource, 'literotica.com/c/', '"'))

            self.authorPageUrl = sandwichMaker(self.pageSource,'<!-- ! --></span><a href="','"')
            self.getDateFromAuthor()

            print('[Retrieved]   Submission Metadata')

        self.pageText = sandwichMaker(self.pageSource,'b-story-body-x x-r15"><div>','</div>')

    def downloadPreClassic(self):
        # get metadata on first loop
        if self.currentPage == 1:

            title = sandwichMaker(self.pageSource,'<h1>','</h1>')
            self.title = title.replace('&quot;','"').replace('&#x27;',"'").replace('&amp;','&').replace('/','-')

            self.pages = int(sandwichMaker(self.pageSource,'"b-pager-caption">',' Pages'))
            self.username = sandwichMaker(self.pageSource,'page=submissions">','</a>')
            self.description = sandwichMaker(self.pageSource,'name="description" content="','"/')
            self.category = sandwichMaker(self.pageSource,'>','<',self.pageSource.find('category.php'))

            self.authorPageUrl = sandwichMaker(self.pageSource,'class="b-story-user"><a href="','">')
            self.getDateFromAuthor()

            print('[Retrieved]   Submission Metadata')

        self.pageText = sandwichMaker(self.pageSource,'class="b-story-body">','</div>')

    def downloadPostOriginal(self):

        if self.currentPage == 1:

            self.title = sandwichMaker(self.pageSource,'<h1>','</h1>')
            self.title = self.title.replace('&quot;','"').replace('&#x27;',"'").replace('&amp;','&').replace('/','-')
            print('Title: ' + self.title)

            self.pages = self.pageSource.count(self.slug + '&amp;page=')
            if self.pages == 0: self.pages = 1
            self.username = sandwichMaker(self.pageSource,'page=submissions">','</a>')
            self.description = sandwichMaker(self.pageSource,'name="description" content="','"')
            self.category = sandwichMaker(self.pageSource,'>','<',self.pageSource.find('category.php'))

            self.authorPageUrl = sandwichMaker(self.pageSource,'by <a href="','"')
            self.getDateFromAuthor()

            print('[Retrieved]   Submission Metadata')

        self.pageText = '<p>' + sandwichMaker(self.pageSource,'<div id="content"><p>','</p>') + '</p>'

    def downloadOriginal(self):

        if self.currentPage == 1:

            self.title = sandwichMaker(self.pageSource,'Helvetica"><strong>','<')
            self.title = self.title.replace('&quot;','"').replace('&#x27;',"'").replace('&amp;','&').replace('/','-')
            print('Title: ' + self.title)

            self.pages = self.pageSource.count(self.slug + '&amp;page=')
            if self.pages == 0: self.pages = 1
            self.username = sandwichMaker(self.pageSource,'page=submissions">','</a>',self.pageSource.find('Helvetica"><strong>'))
            self.description = sandwichMaker(self.pageSource,'name="description" content="','"')
            self.category = sandwichMaker(self.pageSource,'>','<',self.pageSource.find('category.php'))

            self.authorPageUrl = sandwichMaker(self.pageSource,'by <a href="','"')
            self.getDateFromAuthor()

            print('[Retrieved]   Submission Metadata')

        self.pageText = '<p>' + sandwichMaker(self.pageSource,'<font size="2"><br/>','</font>') + '</p>'

    # PRIMARY METHODS
    def download(self):
    # collect all data needed to export the submission, calling the appropiate download functions for each scheme

        print(f"\n[Downloading] {cleanTitle(self.url)} ({getSite(self.url)})")
        print(f"[URL]         {self.url}")

        # loop through each page of submission and gather all page text
        while self.currentPage <= self.pages:

            self.getPageSource()

            if self.skip == 1: return

            self.getScheme()

            # call relevant method to extract page text
            if self.scheme == 'Modern': self.downloadModern()
            if self.scheme == 'Classic': self.downloadClassic()
            if self.scheme == 'Pre-Classic': self.downloadPreClassic()
            if self.scheme == 'Post-Original': self.downloadPostOriginal()
            if self.scheme == 'Original': self.downloadOriginal()

            if self.skip == 1: return

            # extract and save any audio files (only for audio categories)
            if self.category == 'Audio' or self.category == 'Poetry With Audio':
                self.pageText = getAudio(self.pageText, self.pageSource, self.title, self.username)

            # process page text for illustration categories
            if self.category == 'Adult Comics' or self.category == 'Erotic Art':
                self.pageText = cleanIllustrationSource(self)

            self.text += self.pageText

            print(f"[Saved]       Page {self.currentPage} of {self.pages} ({self.scheme} Site Scheme)")

            self.currentPage += 1

        self.wordCount = wordCount(self.text)

        # send to get images function to extract images from <img> tags
        self.text = getImages(self.text, self.username)

    def build(self):
        # prepare all collected submission data for export

        self.output = getOutput(self)
        self.path = getPath(self.username)
        self.filename = getFilename(self.date,self.title)

    def export(self):
        export(self.path, self.filename, self.output)

class xnxx:
    
    def __init__(self, url):
        # immediately defined
        self.url = url
        self.publisher = "xnxx"

        self.pageSource = ''

        # submission metadata
        self.title = ''
        self.username = ''
        self.series = ''
        self.date = ''
        self.description = ''
        self.category = ''

        # submission text attributes
        self.text = ''
        self.wordCount = ''

        self.skip = 0 # skipping flag if there is a problem getting page source
        # build items
        self.output = ''
        self.path = ''
        self.filename = ''

    # PRIMARY METHODS
    def download(self):
    # collect all data needed to export the submission

        print(f"\n[Downloading] {cleanTitle(self.url)} ({getSite(self.url)})")
        print(f"[URL]         {self.url}")
        
        self.pageSource = getSource(self.url)
        if self.pageSource == 'skip': self.skip = 1; return
        
        title = sandwichMaker(self.pageSource,'<h2>\n','<span',self.pageSource.find('<div class="story_info">'))
        if title == -1: self.title = 'unkown_title'
        else:
            self.title = (' ').join(list(filter(None, title.replace('\t','').split(' '))))
 
        self.username = sandwichMaker(self.pageSource,'">','</a>', self.pageSource.find('/profile'))
        if self.username == -1: self.username = 'unknown_author'
        
        description = sandwichMaker(self.pageSource,'</h2>\n','</div>',self.pageSource.find('Introduction:'))
        if description == -1: self.description = ''
        else:
            self.description = (' ').join(list(filter(None, description.replace('\t','').split(' '))))

        category = sandwichMaker(self.pageSource,'<div class="top_info">\n','</div>').replace('\t','')
        self.category = (' ').join(list(filter(None, category.split(' '))))
            
        date = sandwichMaker(self.pageSource,'Posted ','<div id="report">',self.pageSource.find('<div class="story_date">'))
        if date == -1: self.date = '0000-00-00'
        else:
            date = list(filter(None, date.replace('\t','').split(' ')))
            if 'ago' in date: self.date = '0000-00-00'
            else:
                self.date = ('-').join([date[-1],getMonth(date[-2]),'0' + date[1][:-2] if int(date[1][:-2])<10 else date[1][:-2]])
        
        self.text = sandwichMaker(self.pageSource, '<div class="block_panel">', '<!-- VOTES -->', self.pageSource.find('<!-- CONTENT -->'))

        self.wordCount = wordCount(self.text)

    def build(self):
    # prepare all retrieved submission data for export

        self.output = getOutput(self)
        self.path = getPath(self.username)
        self.filename = getFilename(self.date,self.title)

    def export(self):
        export(self.path, self.filename, self.output)

# HELPER FUNCTIONS

def sandwichMaker(textSource, topBread, bottomBread, start=0, reverse=0):
    # return part of a string between two known substrings (the 'filling' of a sandwich)
    # returns -1 if cannot find substring

    if reverse == 1:
        begin = textSource.rfind(topBread) + len(topBread)
    else:
        begin = textSource.find(topBread, start) + len(topBread)
    if begin == (-1 + len(topBread)): return -1
    end = textSource.find(bottomBread, begin)
    filling = textSource[begin:end]
    return filling

def cleanTitle(url):
    # convert the submission url into a temp title to display while downloading
    
    # xnxx url
    if 'sexstories.com' in url:
        if url.endswith('/'): url = url[:-1]
        return url.split('/')[-1].replace('_', ' ').title()
    
    # Original Literotica url (no title in url, use number)
    if 'literotica.com/stories/showstory.php' in url:
        return f"Title Unknown ({url.split('?')[-1]})"

    # all other Literotica schemes
    if 'literotica.com' in url:
        cleanTitle = url.split('/')[-1].split('-')

        # remove unimportant numbers from the end of the title
        if len(cleanTitle) > 1:
            if cleanTitle[-1].isdigit() and cleanTitle[-2].isdigit():
                del cleanTitle[-1]
            if 'ch' not in cleanTitle and 'pt' not in cleanTitle:
                if cleanTitle[-1].isdigit(): del cleanTitle[-1]

        # convert back to strings
        return (' ').join(cleanTitle).title()

def getSource(url, attempts=0):
    # get the webpage html source from a given url and sort all errors

    # certain errors require a retry
    if attempts == 7:
        print('Too many attempts. Try again later.')
        return 'skip'

    try:
        return urllib.request.urlopen(url).read().decode('utf-8')

    # catch any error and disply some reasons, then either return or retry
    except urllib.error.HTTPError as e:
        print('HTTPError - Code: ' + str(e.code) + ' Reason: ' + str(e.reason) + '. ')
        print('The following URL caused an error:')
        print(url)
        if e.code == 410:
            return 'skip'
        if e.code == 404:
            if '//english.' in url:
                # original and post-original schemes might need this change
                print('Trying a different URL of the same page...')
                url = url.replace('//english.','//www.')
                return getSource(url, attempts)
            return 'skip'
        if e.code == 503:
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)
        if e.code == 504:
            print('Gateway Time-out. Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)
        if e.code == 502:
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)

    except urllib.error.URLError as e:
        print('URLError - Reason: ' + str(e.reason) + '.')
        print('The following URL caused an error:')
        print(url)
        if '104' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)
        if '110' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)
        if '111' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)
        if '-3' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return getSource(url, attempts)
        if '113' in str(e.reason):
            print('URL should be in format "https://www.literotica.com/*/... (* = s, p, or i)"')
            return 'skip'

    except ValueError as e:
        print('ValueError on the following URL')
        print(url)
        print('Literotica URLs should be in the format "https://www.literotica.com/*/... (* = s, p, or i)"')
        return 'skip'

    except http.client.IncompleteRead:
        print('Error: Incomplete Read on the following URL:')
        print(url)
        print('Retrying in 5 seconds...')
        time.sleep(5)
        attempts += 1
        return getSource(url, attempts)

    return

def getPath(username):
    # return save path for final export (no spaces in filenames)

    return os.path.join(origCwd, 'litstash-saves', username.replace(' ','_'))

def getSite(url):
    # check if the submission is from xnxx, literotica, wayback machine

    if 'web.archive.org' in url:
        if 'literotica.com' in url: return 'Wayback Machine/Literotica'
        if 'sexstories.com' in url: return 'Wayback Machine/xnxx'
    else:
        if 'literotica.com' in url: return 'Literotica'
        if 'sexstories.com' in url: return 'xnxx'
    return 'unknown'

def cleanIllustrationSource(obj):
    # remove unimportant html tags from page source of illustrations

    # need to extract pageText iff obj is from literotica (not wayback machine)
    if not 'web.archive.org' in obj.url:
        pageText = sandwichMaker(obj.pageSource,'<div class="aa_ht">','<div class="aa_hv aa_hy">')
    else:
        pageText = obj.pageText

    # remove all <div> and <div *> tags
    counter = 0 # safety against accidental infinit loop
    while pageText.count('<div ') > 0:
        pageText = pageText.replace(sandwichMaker(pageText,'<div ','>'),'')
        pageText = pageText.replace('<div >','')
        counter += 1
        if counter > 1000: break

    pageText = pageText.replace('<div>','')
    pageText = pageText.replace('</div>','')

    # remove all <p *> tags
    counter = 0
    while pageText.count('<p ') > 0:
        pageText = pageText.replace(sandwichMaker(pageText,'<p ','>'),'')
        pageText = pageText.replace('<p >','<p>')
        counter += 1
        if counter > 1000: break

    # remove all <a href=...> tags
    counter = 0
    while pageText.count('<a href=') > 0:
        pageText = pageText.replace(sandwichMaker(pageText,'<a ','>'),'')
        pageText = pageText.replace('<a >','')
        counter += 1
        if counter > 1000: break

    pageText = pageText.replace('</a>','')

    # change p to f in image names (gives higher res image)
    start = 0
    for i in range(pageText.count('<img src="')):
        imageName = sandwichMaker(pageText,'<img src="','"',start).split('/')[-1]
        i = pageText.find(imageName)
        pageText = pageText[:i]+'f'+pageText[i+1:]
        start = i

    # remove any extra '<' or '>'
    pageText = pageText.replace('<<','<').replace('<<<','<').replace('>>>','>').replace('>>','>')

    # remove <li> and <ul> tags, there shouldn't be bullet points
    pageText = pageText.replace('<li>','').replace('</li>','').replace('<ul id="illustra">','').replace('</ul>','')

    # return the pageText of an ordinary illustrated story
    return pageText

def getCategory(category):
    # dictionary to convert from url slug of categories to real category names

    categories = {
        'anal-sex-stories' : 'Anal', 'audio-sex-stories' : 'Audio', 'bdsm-stories' : 'BDSM',
        'celebrity-stories' : 'Celebrities & Fan Fiction', 'chain-stories' : 'Chain Stories',
        'erotic-couplings' : 'Erotic Couplings', 'erotic-horror' : 'Erotic Horror',
        'exhibitionist-voyeur' : 'Exhibitionist & Voyeur', 'fetish-stories' : 'Fetish',
        'first-time-sex-stories' : 'First Time', 'gay-sex-stories' : 'Gay Male',
        'group-sex-stories' : 'Group Sex', 'adult-how-to' : 'How To',
        'adult-humor' : 'Humor & Satire', 'illustrated-erotic-fiction' : 'Illustrated',
        'taboo-sex-stories' : 'Incest/Taboo', 'interracial-erotic-stories' : 'Interracial Love',
        'lesbian-sex-stories' : 'Lesbian Sex', 'erotic-letters' : 'Letters & Transcripts',
        'loving-wives' : 'Loving Wives', 'mature-sex' : 'Mature', 'mind-control' : 'Mind Control',
        'non-english-stories' : 'Non-English', 'non-erotic-stories' : 'Non-Erotic',
        'non-consent-stories' : 'NonConsent/Reluctance', 'non-human-stories' : 'NonHuman',
        'erotic-novels' : 'Novels and Novellas', 'reviews-and-essays' : 'Reviews & Essays',
        'adult-romance' : 'Romance', 'science-fiction-fantasy' : 'Sci-Fi & Fantasy',
        'masturbation-stories' : 'Toys & Masturbation',
        'transgender-crossdressers' : 'Transgender & Crossdressers',
        'erotic-poetry' : 'Erotic Poetry', 'illustrated-poetry' : 'Illustrated Poetry',
        'non-erotic-poetry' : 'Non-Erotic Poetry', 'erotic-audio-poetry' : 'Poetry With Audio',
        'adult-comics' : 'Adult Comics', 'erotic-art' : 'Erotic Art'
        }

    return categories[category] if category in categories else category

def getKind(url):
    # check if submission is a story, poem, or illustration

    if '/s/' in url or '/stories/showstory.php' in url or 'sexstories.com' in url: 
        return 'Story'
    elif '/i/' in url: return 'Illustration'
    elif '/p/' in url: return 'Poem'
    else: return 'unknown'

def getMonth(month):
    month_dict = {
    'January' : '01','February' : '02','March' : '03','April' : '04','May' : '05','June' : '06',
    'July' : '07','August' : '08','September' : '09','October' : '10','November' : '11','December' : '12'
    }
    
    return month_dict[month]

def wordCount(text):
    # approximate number of words in the submission text

    return len(text.split())

def cleanHexCodes(text):
    # remove hexcodes from strings and replace with true character

    text = text.replace('&#x27;',"'").replace('&#x21;','!').replace('&#x22;','"').replace('&#x23;','#')
    text = text.replace('&#x25;','%').replace('&#x26;','&').replace('&#x28;','(').replace('&#x29;',')')
    text = text.replace('&#x2a;','*').replace('&#x2c;',',').replace('&#x2e;','.').replace('&#x2f;','/')
    text = text.replace('&#x3a;',':').replace('&#x3b;',';').replace('&#x3f;','?').replace('&#x40;','@')
    return text

def cleanUrl(url):
    # ensure each url begins with https:// and a proper domain (some scraped urls are incomplete)
    
    # detect and fix xnxx url
    if '/story/' in url:
        if not 'sexstories.com' in url: url = 'https://www.sexstories.com' + url      
    
    # detect and fix literotica url (if not xnxx, it's literotica)
    if not 'sexstories.com' in url:
        if not 'literotica.com' in url: url = 'https://www.literotica.com' + url

    # detect and fix Wayback Machine url
    if '/web/' in url:
        if not 'web.archive.org' in url: url = 'https://web.archive.org' + url

        # insert 'im_' after retrieval date in wayback machine urls to create direct download links to resources
        # specific to Wayback captures of literotica audios and illustrations
        if '/illustra/' in url or '/audio/' in url:
            url = url.replace('if_/','im_/')
            if 'im_/' not in  url:
                i = url.rfind('/http')
                url = url[:i]+'im_'+url[i:]
            
    # ensure that each url begins with https:// before requesting source
    if url.startswith('http://'): url = 'https://' + url[7:]
    elif url.startswith('//'): url = 'https:' + url
    elif url.startswith('www'): url = 'https://' + url
    
    if not url.startswith('https://'): url = 'https://' + url
    
    return url

def export(path,filename,output):
    # save final export to file

    # check if file path exists, create directories, and change working directory
    if not os.path.isdir(path): os.makedirs(path, exist_ok=True)
    os.chdir(path)

    # output the extracted submission
    f = open(filename, 'w', encoding='utf-8')
    f.write(output)
    f.close()

    # return to original working directory
    os.chdir(origCwd)

    print(f"[Finished]    Exported to: {os.path.join(path, filename)}")

def getOutput(obj):
    # create the ultimate string which will be the final output

    header = (
        f'<title>{obj.title}</title>\n\n'
        f'<meta name="title" content="{obj.title}">\n'
        f'<meta name="author" content="{obj.username}">\n'
        f'<meta name="tags" content="{obj.category}">\n'
        f'<meta name="series" content="{obj.series}">\n'
        f'<meta name="publisher" content="{obj.publisher}">\n'
        f'<meta name="pubdate" content="{obj.date}">\n'
    )

    body_header = (
        f'<font size = "1">{obj.url}</font><br>\n'
        f'<font size = "5"><b>{obj.title}</b></font><br>\n'
        f'<font size = "4">{obj.username}</font><br>\n'
        f'<font size = "1">{obj.wordCount} words  ||  {obj.category}  ||  {obj.date}</font><br>\n'
        f'<font size = "3"><i>{obj.description}</i></font><br>\n'
        f'<font><b>- - - - - - - - - - - - - -</b></font><br>\n'
    )

    output = (
        f'<html>\n\n'
        f'<head>\n\n'
        f'{header}\n'
        f'</head>\n\n'
        f'<body>\n\n'
        f'{body_header}\n'
        f'{obj.text}\n\n'
        f'</body>\n\n'
        f'</html>\n'
    )

    return cleanHexCodes(output)

def getFilename(date, title):
    # prepare filename of export (include date for sorting, no spaces and minimal puncuation)

    title = title.replace('.','').replace(' ','-')
    # remove puncuation marks from title
    title = title.replace('---','-').replace('--','-').replace(',','').replace('!','').replace('?','')
    title = title.replace(':','').replace(';','').replace("'",'').replace('"','').replace('|','')
    title = title.replace('[','').replace(']','').replace("<",'').replace('>','').replace('*','')
    title = title.replace('/','-').replace('\\','-')
    return f"{date}_{title}.html"

def saveFile(fileUrl, fileName, savePath, attempts=0):
    # download a resource (image or audio file), sort errors, retry with adjusted URLs

    # allow 5 retries
    if attempts == 5:
        print('Too many attempts. Try again later.')
        return 'skip'

    success = 0

    # check if directory tree exists, create it, and change working directory
    if not os.path.isdir(savePath): os.makedirs(savePath, exist_ok=True)
    os.chdir(savePath)

    try:
        urllib.request.urlretrieve(fileUrl,fileName)
        success = 1 # success flag

    # create exceptions to catch any error and disply some reasons, then either return or retry
    except urllib.error.HTTPError as e:
        print('HTTPError - Code: ' + str(e.code) + ' Reason: ' + str(e.reason) + '. ')
        print('The following URL caused an error:')
        print(fileUrl)
        if e.code == 410:
            print('Skipping this file...')
            pass
        if e.code == 404:
            if '//english.' in fileUrl: # some original and post-original scheme files might need this
                print('Trying a different URL of the same file...')
                fileUrl = fileUrl.replace('//english.','//www.')
                return saveFile(fileUrl, fileName, savePath, attempts)
            print('Skipping this file...')
            pass
        if e.code == 503:
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)
        if e.code == 504:
            print('Gateway Time-out. Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)
        if e.code == 502:
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)

    except urllib.error.URLError as e:
        print('URLError - Reason: ' + str(e.reason))
        print('The following URL caused an error:')
        print(fileUrl)
        if 'incomplete' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)
        if '104' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)
        if '110' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)
        if '111' in str(e.reason):
            print('Retrying in 5 seconds...')
            time.sleep(5)
            attempts += 1
            return saveFile(fileUrl, fileName, savePath, attempts)
        if '113' in str(e.reason):
            print('Skipping this file...')
            pass

    except InvalidURL as e:
        print('InvalidURL: The following URL is invalid...')
        print(fileUrl)
        print(f'Reason: {e.reason}')
        print('Skipping this file...')
        pass

    except ValueError as e:
        print('ValueError: The following file URL is unrecognized...')
        print(fileUrl)
        print('Skipping this file...')
        pass

    except http.client.IncompleteRead:
        print('Error: Incomplete Read on the following URL:')
        print(fileUrl)
        print('Retrying in 5 seconds...')
        time.sleep(5)
        attempts += 1
        return saveFile(fileUrl, fileName, savePath, attempts)

    os.chdir(origCwd) # change back to original working directory
    return success # return success flag

def getAudio(pageText, pageSource, title, username):
    # retrieve audio files from page text, or from embedded player (modern scheme)

    audioTypes = ['mp3','ogg','wav','aiff','m4a','flac', 'ram']
    savePath = os.path.join(getPath(username), 'audios')
    urlCount = pageText.count('<a href="')
    audioCount = pageSource.count('<audio src="')
    audioUrls = []
    searchStart = 0
    savedCount = 0
    skippedCount = 0

    # search pageText for audio links (if linked within it rather than embedded below)
    if urlCount == 0: pass
    else:

        for i in range(urlCount):
            url = sandwichMaker(pageText,'a href="','"',searchStart)
            if url.split('.')[-1] in audioTypes: audioUrls.append(url)
            searchStart = pageText.find(url)

        if len(audioUrls) == 0: pass
        else:
            print(f"[Detected]    {len(audioUrls)} audio(s) to download")
            for audioUrl in audioUrls:

                audioName = audioUrl.split('/')[-1]
                pageText = pageText.replace(audioUrl,'audios/'+audioName)

                audioUrl = cleanUrl(audioUrl)

                # download the audio file
                success = saveFile(audioUrl, audioName, savePath,)
                if success:
                    savedCount += 1
                    print(f"[Retrieved]   {savedCount} of {len(audioUrls)} audio(s) ({skippedCount} Skipped)")

                # if failure, attempt something else
                elif 'web.archive.org' in audioUrl:
                    print('Trying a different URL of the same file...')
                    audioUrl = audioUrl.replace('im_/','if_/')
                    success = saveFile(audioUrl, audioName, savePath,)
                    if success:
                        savedCount += 1
                        print(f"[Retrieved]   {savedCount} of {len(audioUrls)} audio(s) ({skippedCount} Skipped)")
                    else: skippedCount += 1
                else: skippedCount += 1

            return pageText

    # search pageSource for audio (if embedded below pageText rather than linked within it)
    if audioCount == 0: pass
    else: print(f"[Detected]    {audioCount} audio(s) to download")

    for i in range(audioCount):

        audioUrl = sandwichMaker(pageSource,'<audio src="','"', searchStart)
        audioName = audioUrl.split('/')[-1]
        pageText = pageText + f'\n<br><br><a href="audios/{audioName}">{title}</a>'
        searchStart = pageSource.find(audioName)

        audioUrl = cleanUrl(audioUrl)

        success = saveFile(audioUrl, audioName, savePath)
        if success:
            savedCount += 1
            print(f"[Retrieved]   {savedCount} of {audioCount} audio(s)  ({skippedCount} Skipped)")
        elif 'web.archive.org' in audioUrl:
            print('Trying a different URL of the same file...')
            audioUrl = audioUrl.replace('im_/','if_/')
            success = saveFile(audioUrl, audioName, savePath,)
            if success:
                savedCount += 1
                print(f"[Retrieved]   {savedCount} of {len(audioUrls)} audio(s)  ({skippedCount} Skipped)")
            else: skippedCount += 1
        else: skippedCount += 1

    return pageText # return pageText with audio urls modified to be local

def getImages(text, username):
    # retrieve images from within final text

    imageCount = text.count('<img src="')
    if imageCount == 0: return text
    else: print(f"[Detected]    {imageCount} image(s) to download")

    searchStart = 0
    savedCount = 0
    skippedCount = 0
    savedUrls = []
    savePath = os.path.join(getPath(username), 'images')

    for i in range(imageCount):

        imageUrl = sandwichMaker(text,'<img src="','"',searchStart)
        if imageUrl == -1: print('No more images to save.'); return text
        imageName = imageUrl.split('/')[-1]
        text = text.replace(imageUrl,'images/'+imageName, 1) # modify image urls to be local
        searchStart = text.rfind(imageName)

        # attempt the save the image
        imageUrl = cleanUrl(imageUrl)
        if imageUrl not in savedUrls:
            success = saveFile(imageUrl,imageName,savePath)

        if success:
            savedCount += 1
            savedUrls.append(imageUrl)
            print(f"[Retrieved]   Image {savedCount} of {imageCount}  ({skippedCount} Skipped)")

        # if f-file is unavailable, try to save p-file (lower res)
        elif '/illustra/' in imageUrl and imageName.startswith('f'):

            # attempt the low res p version
            print('Attempting to save a lower-resolution version...')
            imageName_p = 'p' + imageName[1:]
            imageUrl_p = imageUrl[:imageUrl.rfind('/')+1] + imageName_p

            success = saveFile(imageUrl_p,imageName_p,savePath)

            if success:
                savedCount += 1
                savedUrls.append(imageUrl)
                text = text.replace(imageName,imageName_p)
                print(f"[Retrieved]   Image {savedCount} of {imageCount}  ({skippedCount} Skipped)")
            else: skippedCount +=1

        else: skippedCount += 1

    return text # return final text with local image urls (images/...)

# PRIMARY FUNCTIONS

def getSubmission(url):
    # initiate the process of downloading a given submission

    # ensure url begins with 'https://'
    url = cleanUrl(url)
    
    # each submission is an object while being downloaded
    site = getSite(url)
    if site == 'Literotica': obj = literotica(url) # create literotica object
    elif site == 'xnxx': obj = xnxx(url) # create xnxx object
    elif site == 'Wayback Machine/Literotica': obj = waybackMachineLit(url) # create wayback machine object
    elif site == 'Wayback Machine/xnxx': obj = xnxx(url) # create wayback machine object
    else: 
        print('Unknown website - Skipping submission...')
        return 0
        
    obj.download() # retrieve all metadata, page text, audios and images for submission
    if obj.skip == 1: print('Skipping submission...'); del obj; return 0 # obey skip flag
    else:
        obj.build() # compile final output string
        obj.export() # export final string to html file
        del obj
        return 1

def getList():
    # show list of all detected submissions, send selections to be downloaded

    savedCount = 0
    skippedCount = 0

    if len(downloadList) == 0:
        print('No submissions detected. Quitting...')
        raise SystemExit

    print(f"Detected {len(downloadList)} unique submission(s) in total")

    if len(downloadList) == 1: # automatically download single stories
        getSubmission(downloadList[0])
        raise SystemExit

    # display list of multiple urls
    for i in range(len(downloadList)):
        print(' '*(len(str(len(downloadList)))-len(str(i+1))),end='')
        print(f" {i+1} : [{getKind(downloadList[i])}] {cleanTitle(downloadList[i])} ({getSite(downloadList[i])})")

    # if user included -a flag, automatically download all detected submissions
    if a == 0:
        print('--> Select submissions to download (eg: 1 3 7 12, 2-9, a = all, q = quit)')
        selection = input('--> ').strip()
    if a == 1: selection = 'a'

    # process user input
    if selection == 'q': raise SystemExit

    if selection == 'a':
        for submission in downloadList:
            finished = getSubmission(submission)
            if finished == 0:
                skippedCount += 1
            if finished == 1:
                savedCount += 1
                print(f"[Completed]   {savedCount} of {len(downloadList)} Submissions ({skippedCount} Skipped)")
        raise SystemExit

    if ' ' in selection:
        selectionList = selection.split(' ')
        for number in selectionList:
            finished = getSubmission(downloadList[int(number)-1])
            if finished == 0:
                skippedCount += 1
            if finished == 1:
                savedCount += 1
                print(f"[Completed]   {savedCount} of {len(selectionList)} Submissions ({skippedCount} Skipped)")
        raise SystemExit

    if '-' in selection:
        numbers = selection.split('-')
        for i in range(int(numbers[0])-1,int(numbers[1])):
            finished = getSubmission(downloadList[i])
            if finished == 0:
                skippedCount += 1
            if finished == 1:
                savedCount += 1
                print(f"[Completed]   {savedCount} of {int(numbers[1])-int(numbers[0])+1} Submissions ({skippedCount} Skipped)")
        raise SystemExit

    if selection.isdigit():
        getSubmission(downloadList[int(selection)-1])
        raise SystemExit

def scanForUrls(url):
    # scan any webpage for literotica or xnxx submissions

    print('Scanning given page for Submissions... ', end='')
            
    xnxxStoryCount = 0
    storyCount = 0
    originalStoryCount = 0
    illustrationCount = 0
    poemCount = 0
    i = 0

    pageSource = getSource(url)

    totalXnxxStories = pageSource.count('/story/')
    totalStories = pageSource.count('literotica.com/s/')
    totalOriginalStories = pageSource.count('literotica.com/stories/showstory.php')
    totalIllustrations = pageSource.count('literotica.com/i/')
    totalPoems = pageSource.count('literotica.com/p/')

    # scan for xnxx story urls
    i = 0
    while xnxxStoryCount < totalXnxxStories:

        i = pageSource.find('/story/', i)

        # find beginning and end of story URL
        while pageSource[i-1] != '"': i -= 1
        beg = i
        while pageSource[i] != '"': i += 1
        end = i

        url = cleanUrl(pageSource[beg:end])

        if url not in downloadList:
            downloadList.append(url)

        xnxxStoryCount += 1

    # scan for story urls
    i = 0
    while storyCount < totalStories:

        i = pageSource.find('literotica.com/s/', i)

        # find beginning and end of story URL
        while pageSource[i-1] != '"': i -= 1
        beg = i
        while pageSource[i] != '"': i += 1
        end = i

        url = cleanUrl(pageSource[beg:end])

        # do not confuse a link to the general story category with a submission
        if url.endswith('/s/'):
            totalStories -= 1
            storyCount -= 1
        else:
            if url not in downloadList:
                downloadList.append(url)

        storyCount += 1

    # scan for story urls (original scheme used different urls) (wayback machine)
    i = 0
    while originalStoryCount < totalOriginalStories:

        i = pageSource.find('literotica.com/stories/showstory.php', i)

        # find beginning and end of URL
        while pageSource[i-1] != '"': i -= 1
        beg = i
        while pageSource[i] != '"': i += 1
        end = i

        url = cleanUrl(pageSource[beg:end])

        if url not in downloadList:
            downloadList.append(url)

        originalStoryCount += 1

    # scan for illustration urls
    i = 0
    while illustrationCount < totalIllustrations:

        i = pageSource.find('literotica.com/i/', i)

        # find beginning and end of URL
        while pageSource[i-1] != '"': i -= 1
        beg = i
        while pageSource[i] != '"': i += 1
        end = i

        url = cleanUrl(pageSource[beg:end])

        # do not confuse a link to the illustration category with a submission
        if url.endswith('/i/'):
            totalIllustrations -= 1
            illustrationCount -= 1
        else:
            if url not in downloadList:
                downloadList.append(url)

        illustrationCount += 1

    # scan for poem urls
    i = 0
    while poemCount < totalPoems:

        i = pageSource.find('literotica.com/p/', i)

        # find beginning and end of poem URL
        while pageSource[i-1] != '"': i -= 1
        beg = i
        while pageSource[i] != '"': i += 1
        end = i

        url = cleanUrl(pageSource[beg:end])
        
        # do not confuse a link to the poetry category with a submission
        if url.endswith('/p/'):
            totalPoems -= 1
            poemCount -= 1
        else:
            if url not in downloadList:
                downloadList.append(url)

        poemCount += 1

    totalCount = xnxxStoryCount+storyCount+illustrationCount+poemCount

    if totalCount != 0: print(f"found {totalCount}")
    else: print('')

def scanAuthorPage(url):
    # collect links to all submissions by given author url and append to downloadList
    print("Author Page Detected")
    
    urlComponents = url.split("/")
    username = str(urlComponents[urlComponents.index('authors')+1])
    
    print("[Username]   " + username)
    
    # avoid trying to download favorites
    if '/favorites/' in url:
        print ('''
Unfortunately, Litstash does not currently support batch downloading favorites lists from the new author page layout.
Try submitting a link to a Wayback Machine capture of the same favorites page with the previous layout.
''')
        return 0
    
    # get and display author userID
    print("[UserID]     ", end="")
    pageSource = getSource(cleanUrl(url))
    userId = sandwichMaker(pageSource, 'userid:', ',')
    if not userId == -1:
        print(userId)
    else:
        print("") 
        return 0
    
    # retrieve submission list from author API
    print("[Scanning]   Submission List")
    currentPage = 1
    lastPage = 1
    storyUrlList = []
    
    # loop through multiple pages of API if user has more than 50 submissions
    while lastPage >= currentPage:

        url = 'https://literotica.com/api/3/users/' + userId + '/stories?params={"page":' + str(currentPage) + '}'
        authorApiData = json.loads(getSource(url))
        lastPage = int(authorApiData['last_page'])
        
        submissionData = authorApiData['data']
        
        for submission in submissionData:
            if submission['type'] == 'story': storyUrlList.append('https://www.literotica.com/s/' + submission['url'])
            if submission['type'] == 'audio': storyUrlList.append('https://www.literotica.com/s/' + submission['url'])
            if submission['type'] == 'poem': storyUrlList.append('https://www.literotica.com/p/' + submission['url'])
            if submission['type'] == 'illustra': storyUrlList.append('https://www.literotica.com/i/' + submission['url'])
            else: pass
            
        print("[Done]       Page " + str(currentPage) + " of " + str(lastPage))
        currentPage += 1

    print("")
    # append all detected submissions to downloadList
    for url in storyUrlList: 
        if url not in downloadList: 
            downloadList.append(url)
    
def parseArgs(args):
    # parse all user arguments from the command line (urls or optional flags)
    
    # use 'a' as a toggle to auto-download all submissions if -a in arguments
    global a
    a = 0

    if len(args) == 0: print(usage); raise SystemExit

    for arg in args:

        if arg == '-h' or arg == '--help':
            print(usage)
            raise SystemExit
        elif arg == '-a': a = 1
        elif arg == '--version' or arg == '-v':
            print(version)
            print(updated)
            raise SystemExit
        elif arg.startswith('-') and len(args) == 1:
            print('Not a valid argument. Use --help for usage.')
            raise SystemExit
        elif 'literotica.com/s/' in arg:
            if arg not in downloadList: downloadList.append(arg)
        elif 'literotica.com/i/' in arg:
            if arg not in downloadList: downloadList.append(arg)
        elif 'literotica.com/p/' in arg:
            if arg not in downloadList: downloadList.append(arg)
        elif 'literotica.com/authors/' in arg:
            scanAuthorPage(arg)
        elif 'literotica.com/stories/showstory.php' in arg:
            if arg not in downloadList: downloadList.append(arg)
        elif 'sexstories.com/story/' in arg:
            if arg not in downloadList: downloadList.append(arg)
        else:
            scanForUrls(arg)

    # send downloadList to be comprehended and downloaded
    getList()

# START PROGRAM

def main():
    # entire program runs from this function, handle KeyboardInterrupt error here

    try:
        parseArgs(sys.argv[1:]) # send command line arguments to be parsed

    # if KeyboardInterrupt, exit cleanly
    except KeyboardInterrupt:
        print('\n[Detected] Keyboard Interrupt: Quitting...')
        raise SystemExit

    # NameError is often raised after KeyboardInterrupt, still exit cleanly
    except NameError:
        if 'KeyboardInterrupt' in traceback.format_exc():
            print('\n[Detected] Keyboard Interrupt: Quitting...')
            raise SystemExit
        else:
            raise

if __name__ == "__main__":
    main()
