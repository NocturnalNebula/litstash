#!/usr/bin/env python3

#    LICENSE INFORMATION: GNU GPLv3.0-or-later

#    lit-dl is a program for downloading stories from Literotica.

#    Copyright (C) 2023 NocturnalNebula <nocturnalnebula@proton.me>

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

import urllib.request
import urllib.error
import os
from pathlib import Path

# set or create save directory
def set_directory():
    path = os.getcwd()
    print(
    '''
    SET SAVE DIRECTORY MENU
    -----------------------

    1: Return to Main Menu
    2: Save stories to ~/Documents/lit-dl
    3: Save to Custom Path (will create new directory)
    '''
    )
    action = input('Make a selection (1 - 4): ')

    if action == '1':
        main_menu()

    if action == '2':
        path = os.path.join(os.path.expanduser('~'),'Documents', 'lit-dl')

    if action == '3':
        path = Path(input('Save Directory: '))

    if not os.path.exists(path):
        os.mkdir(path)

    os.chdir(path)
    main_menu()

# scrape webpage source code (will retry if URL is good but connection fails)
def get_page_source(url, attempts = 0):

    if attempts == 3:
        print('Too many attempts. Try again later.')
        return back_to_menu()

    try:
        return urllib.request.urlopen(url).read().decode('utf-8')

    # create exceptions to catch any error and disply some reasons, then either return to menu or retry
    except urllib.error.HTTPError as e:
        print('HTTPError - Code: ' + str(e.code) + ' Reason: ' + str(e.reason) + '. ')
        if e.code == 410:
            print('This Wayback Machine capture does not contain an archive of this story. Try a different capture of the same story URL.')
            return 'skip' if input('Skip this story? ["y" for yes] ').lower() == 'y' else back_to_menu()
        if e.code == 404:
            print('Evidently, that page or story does not exist. Check that the URL is correct.')
            return back_to_menu()
        if e.code == 503:
            print('Service unavailable. Retrying...')
            attempts += 1
            return get_page_source(url, attempts)
        if e.code == 504:
            print('Gateway Time-out. Retrying...')
            attempts += 1
            return get_page_source(url, attempts)

    except urllib.error.URLError as e:
        print('URLError - Reason: ' + str(e.reason) + '. ', end='')
        if '104' in str(e.reason):
            print('Retrying...')
            attempts += 1
            return get_page_source(url, attempts)
        if '110' in str(e.reason):
            print('Retrying...')
            attempts += 1
            return get_page_source(url, attempts)
        if '111' in str(e.reason):
            print('Retrying...')
            attempts += 1
            return get_page_source(url, attempts)
        if '113' in str(e.reason):
            print('URL should be in format "https://www.literotica.com/s/..."')
            return back_to_menu()

    except ValueError as e:
        print('URL should be in format "https://www.literotica.com/s/..."')
        return back_to_menu()

    # if an error is not caught by an exception, return to menu instead of returning 'None'
    back_to_menu()

# download lit story
def download_lit_story(url):

    # print out current story
    print('\nNow downloading: ' + url)

    # initialize variables
    text = ''
    pages = 1
    page_num = 1
    username = ''

    #get story title to use in header and filename
    print('Finding story title...')
    title = url.split('/')[-1].title().replace('-', ' ')

    # loop through and save each page of the story
    while page_num <= pages:

        # call function to scrape html from current page of story
        slug = '?page=' + str(page_num)
        html = get_page_source(url + slug)

        # find number of pages while sraping first page
        if page_num == 1 :
            print('Finding page count...')
            if html.count('a class="l_bJ" href="/s/') == 0:
                pages = 1
            else:
                i = html.rfind('a class="l_bJ" href="/s/')
                while html[i] != '>':
                    i += 1
                pages = html[i+1:i+3]
                pages = int(''.join(c for c in pages if c.isdigit()))

        # get username to use in header
        if username == '':
            print('Finding author username...')
            i = html.find(',"username":"') + 13
            beg = i
            while html[i] != '"':
                i += 1
            end = i
            username = html[beg:end]

        # extract and clean up story text from html string
        html = html.split('<div class="aa_ht">')
        html = html[1].replace('<div>', '').replace('</div>', '')

        # append page text to total story text and go to next page
        text += html
        print('Saved Page ' + str(page_num) + ' of ' + str(pages) + '...')
        page_num += 1

    # create header with story title and username
    header = '<h3>' + title + '</h3><p>' + username + '</p><p>' + url + '</p><p>--------------</p>'

    # export story text to html and finish
    export_to_html(text, title, header)
    return None

# download lit story from wayback url
def download_wb_story(url):

    # print out current story
    print('\nNow downloading: ' + url)

    # initialize variables
    text = ''
    pages = 1
    page_num = 1

    # extract story title from URL for filename and header
    print('Finding story title...')
    title = url.split('/')[-1].title().replace('-', ' ')

    # loop through each page of the story
    while page_num <= pages:

        # complete URL for current page and scrape source
        slug = '?page=' + str(page_num)
        if page_num == 1:
                slug = ''

        # get webpage source for current story page
        html = get_page_source(url + slug)

        # skip current story if encountered error 410 (missing story)
        if html == 'skip':
            print('Skipping this story...')
            return None

        # on first loop (page_num = 1) get total number of pages and username of author
        if page_num == 1:
            # get total pages
            print('Finding page count...')
            i = html.find('Pages:</span>')
            pages = int(''.join(c for c in html[i-4:i-1] if c.isdigit()))

            # get username of author
            print('Finding author username...')
            i = html.find('<meta name="keywords" content="') + 31
            beg = i
            while html[i] != '"':
                    i += 1
            end = i - 1
            key_words = html[beg:end]
            username = key_words.split(', ')[1]

        # extract only the story text from the webpage html
        # chop off any html in wayback toolbar to avoid confusing text
        if '<!-- END WAYBACK TOOLBAR INSERT -->' in html:
            html = html.split('<!-- END WAYBACK TOOLBAR INSERT -->')
            html = html[1]
        beg = html.find('<p>')
        end = html.find('</p>', beg) + 4
        html = html[beg:end]

        # update current story text
        text += html
        print('Saved Page ' + str(page_num) + ' of ' + str(pages) + '...')
        page_num += 1

    # create header with story title and username
    header = '<h3>' + title + '</h3><p>' + username + '</p><p>' + url + '</p><p>--------------</p>'

    # export story text to html and finish
    export_to_html(text, title, header)
    return None

# get list of all author's submissions from wayback page
def get_sub_list(url):
    print('\nFinding list of stories...\n')

    # initialize variables
    stories = []
    saved = 0
    i = 0

    # scrape HTML source
    html = get_page_source(url)

    # count total number of expected stories to find
    count = html.count('://www.literotica.com/s/')

    # search HTML source for links to each story
    while len(stories) < count:

        # start search head at 0 and scan for base story URL
        i = html.find('://www.literotica.com/s/', i, len(html))

        # move search head backward to beginning of story URL and save beginning position
        while html[i] != '"':
            i -= 1
        beg = i+1
        i += 1

        # move search head forward to end of story URL and save end position
        while html[i] != '"':
            i += 1
        end = i

        # ensure that story URL is properly formatted and append to story URL list
        # print out list of numbered story URLs
        if html[beg:end].startswith('https:') == True:
            stories.append(html[beg:end])
            print(str(len(stories)) + ': ' + html[beg:end])
        else:
            stories.append('https:' + html[beg:end])
            print(str(len(stories)) + ': ' + 'https:' + html[beg:end])

    # output number of stories found
    print('\nFound ' + str(len(stories)) + ' stories...')

    # return list of stories
    return stories

# download all wayback stories from author
def download_all_wb_stories(stories, start):
    saved = 0
    for num in range(start-1, len(stories)):
        download_wb_story(stories[num])
        saved += 1
        print('[Finished ' + str(saved) + ' of ' + str(len(stories)-start+1) + ' stories]')
    return None

# download all literotica.com stories from author
def download_all_stories(stories, start):
    saved = 0
    for num in range(start-1, len(stories)):
        download_lit_story(stories[num])
        saved += 1
        print('[Finished ' + str(saved) + ' of ' + str(len(stories)-start+1) + ' stories]')
    return None

# export story to html
def export_to_html(text, title, header):
    print('Exporting HTML file...')
    open(title + '.html', mode='w').write('<html><head><title>' + title + '</title></head><body>' + header + text + '</body></html>')
    print('Finished downloading and exporting ' + title + '.html')
    return None

# display after actions are completed
def back_to_menu():
    action = input('Back to menu? ["y" for yes, "n" to quit] ')
    if action.lower() == 'y':
        main_menu()
    if action.lower() == 'n':
        quit()
    back_to_menu()

# main menu of options
def main_menu():

    print('''

    ██╗     ██╗████████╗              ██████╗ ██╗
    ██║     ██║╚══██╔══╝              ██╔══██╗██║
    ██║     ██║   ██║       █████╗    ██║  ██║██║
    ██║     ██║   ██║       ╚════╝    ██║  ██║██║
    ███████╗██║   ██║                 ██████╔╝███████╗
    ╚══════╝╚═╝   ╚═╝                 ╚═════╝ ╚══════╝

    Version 1.2
    Updated: August 2023

    MAIN MENU
    ---------

    Options for Literotica
    1:  Download Story
    2:  Download all Stories by Author

    Options for the Wayback Machine
    3:  Download Story from the Wayback Machine
    4:  Download all Stories by Author on the Wayback Machine

    5:  Help / About
    6:  Set Save Directory
    7:  Exit
    ''')

    print('Current Save Directory: ' + os.getcwd())
    action = input('Make a selection (1 - 7): ')

    if action == '1':
        url = input('Paste Story URL: ')
        download_lit_story(url)
        back_to_menu()

    if action == '2':
        url = input('Paste User Submission Page URL: ')
        stories = get_sub_list(url)
        start = int(input('Begin downloading at which story? (1 = all) '))
        download_all_stories(stories, start)
        back_to_menu()

    if action == '3':
        url = input('Paste Story URL (from web.archive.org): ')
        download_wb_story(url)
        back_to_menu()

    if action == '4':
        url = input('Paste User Submission Page URL (from web.archive.org): ')
        stories = get_sub_list(url)
        start = int(input('Begin downloading at which story? (1 = all) '))
        download_all_wb_stories(stories, start)
        back_to_menu()

    if action == '5':
        print('\nFull readme available at: https://github.com/NocturnalNebula/lit-dl\n')

        if os.path.isfile('/usr/local/lib/lit-dl/README.md'):
            readme = open('/usr/local/lib/lit-dl/README.md', 'r')
            print(readme.read())
            readme.close()

        if os.path.isfile('README.md'):
            readme = open('README.md', 'r')
            print(readme.read())
            readme.close()

        back_to_menu()

    if action == '6':
        set_directory()
        back_to_menu()

    if action == '7':
        exit()

    else:
        main_menu()

# finally, program starts here
main_menu()
