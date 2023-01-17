#!/usr/bin/env python3



#	LICENSE INFORMATION: GNU GPLv3.0-or-later

#	Literotica Downloader (lit-dl) is a program for downloading stories 
#	from Literotica.

#	Copyright (C) 2023 NocturnalNebula <nocturnalnebula@proton.me>

#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.

#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.

#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.

#			**************************************************
#			██╗     ██╗████████╗              ██████╗ ██╗     	
#			██║     ██║╚══██╔══╝              ██╔══██╗██║     	
#			██║     ██║   ██║       █████╗    ██║  ██║██║     	
#			██║     ██║   ██║       ╚════╝    ██║  ██║██║     	
#			███████╗██║   ██║                 ██████╔╝███████╗	
#			╚══════╝╚═╝   ╚═╝                 ╚═════╝ ╚══════╝	
#			**************************************************

#			Literotica Downloader (lit-dl)
#			Version 1.0
#			Requires: Python 3.x
#			Updated: January 2023

#	Welcome to Literotica Downloader (lit-dl v.1.0), a Python3 tool for downloading stories from Literotica. This command line program will download stories in HTML format from literotica.com and from the "classic" Literotica format accessed through the Wayback Machine. However, very old Wayback Machine captures from before Literotica's site format change around 2012 will cause lit-dl to crash.

#	This program was written in January 2023 as an alternative to other Literotica downloaders which stopped working after Lit changed the format of the site several years ago. As of the time of this writing, lit-dl works nicely with the current format of Literotica.

#	It is capable of downloading individual stories or batch downloading all the story submissions from a particular user. The exported HTML files retain <p>, <br>, bold, italics, and other style tags and look nice on an e-reader. Parsing the HTML to TXT exports would remove these stylistic elements, however, it could be easily done by copy/pasting out of a web browser into a text editor. 

#	This program was created as a fun coding project and because it is much nicer to enjoy these stories on the reading device of our choosing rather than page-by-page in a web browser.

#	Enjoy.

#	INSTALLING / RUNNING THE PROGRAM
#	--------------------------------

#	1) Navigate your command line to the same directory where lit-dl.py is located and run it with: 'python3 lit-dl.py'
#	2) Make a selection from the main menu
#	3) Paste literotica.com URLs and let the lit-dl do the rest
#	4) Stories will be exported in HTML format to the same directory as lit-dl.py

#	TROUBLESHOOTING
#	---------------

#	If the program is not working as expected you should first check a few things.

#	1) Ensure that python3 is installed

#	Windows: https://www.python.org/downloads/windows/
#	MacOS: https://www.python.org/downloads/macos/
#	Linux (Ubuntu Family): Type "sudo apt-get install python3" into the command line. 
#	Linux (Other): If you are using non-Ubuntu Linux I think it is safe to assume you can figure out how to install python3 on your own.

#	2) If you are seeing errors about urllib such as "NameError: name 'urllib' is not defined" you might need to install urllib, although this should not be necessary as urllib is a standard library

#	Try reinstalling python3 first.
#	Try 'pip install urllib'. You will probably need to install pip before you can use it to install urllib.

#	3) It may be necessary that you have execute permissions on lit-dl.py

#	< --- PROGRAM BEGINS BELOW --- >

# import libraries and methods
import urllib.request
import urllib.error

# function to scrape webpage HTML source code (will retry if URL is good but connection fails)
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
	

# function to download lit story
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
	title = str(url.split('/')[-1])

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
	header = '<h3>' + title.title().replace('-', ' ') + '</h3><p>' + username + '</p><p>' + url + '</p><p>--------------</p>'

	# export story text to html and finish
	export_to_html(text, title, header)
	return None
	
# function to download lit story from wayback url
def download_wb_story(url):

	# print out current story
	print('\nNow downloading: ' + url)

	# initialize variables
	text = ''
	pages = 1
	page_num = 1

	# extract story title from URL for filename and header
	print('Finding story title...')
	title = url.split('/')[-1]
	
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
	header = '<h3>' + title.title().replace('-', ' ') + '</h3><p>' + username + '</p><p>' + url + '</p><p>--------------</p>'

	# export story text to html and finish
	export_to_html(text, title, header)
	return None

# function to get list of all author's submissions from wayback page
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

# function to download all wayback stories from author
def download_all_wb_stories(stories, start):
	saved = 0
	for num in range(start-1, len(stories)):
		download_wb_story(stories[num])
		saved += 1
		print('[Finished ' + str(saved) + ' of ' + str(len(stories)-start+1) + ' stories]')
	return None
		
# function to download all literotica.com stories from author
def download_all_stories(stories, start):
	saved = 0
	for num in range(start-1, len(stories)):
		download_lit_story(stories[num])
		saved += 1
		print('[Finished ' + str(saved) + ' of ' + str(len(stories)-start+1) + ' stories]')
	return None

# function to export story to html
def export_to_html(text, title, header):
	print('Exporting HTML file...')
	open(title + '.html', mode='w').write('<html>' + header + text + '</html>')
	print('Finished downloading and exporting ' + title + '.html')
	return None
	
# function to display after actions are completed
def back_to_menu():
	action = input('Back to menu? ["y" for yes, "n" to quit] ')
	if action.lower() == 'y':
		main_menu()
	if action.lower() == 'n':
		quit()
	back_to_menu()

# main menu of options
def main_menu():
	while 1:
		print(
	
'''
	**************************************************
	██╗     ██╗████████╗              ██████╗ ██╗     
	██║     ██║╚══██╔══╝              ██╔══██╗██║     
	██║     ██║   ██║       █████╗    ██║  ██║██║     
	██║     ██║   ██║       ╚════╝    ██║  ██║██║     
	███████╗██║   ██║                 ██████╔╝███████╗
	╚══════╝╚═╝   ╚═╝                 ╚═════╝ ╚══════╝
	**************************************************
	
	Literotica Downloader (lit-dl)
	Version 1.0
	Updated: January 2023
	
	MAIN MENU
	---------
	
	Options for Literotica
	1:  Download Story
	2:  Download all Stories by Author

	Options for the Wayback Machine
	3:  Download Story from the Wayback Machine
	4:  Download all Stories by Author on the Wayback Machine

	5:  Help / About
	6:  Exit
'''
			)					
		action = str(input('Make a selection (1 - 6): '))

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
			print(

'''		
	HELP / ABOUT
	------------
	
Literotica Downloader (lit-dl)
Version 1.0
Requires: Python 3.x
Updated: January 2023

Welcome to Literotica Downloader (lit-dl v.1.0), a Python3 tool for 
downloading stories from Literotica. This command line program will 
download stories in HTML format from literotica.com and from the 
"classic" Literotica format accessed through the Wayback Machine. 
However, very old Wayback Machine captures from before Literotica's 
site format change around 2012 will cause lit-dl to crash.

This program was written in January 2023 as an alternative to other 
Literotica downloaders which stopped working after Lit changed the 
format of the site several years ago. As of the time of this writing, 
lit-dl works nicely with the current format of Literotica.

It is capable of downloading individual stories or batch downloading 
all the story submissions from a particular user. The exported HTML files 
retain <p>, <br>, bold, italics, and other style tags and look nice on 
an e-reader. Parsing the HTML to TXT exports would remove these stylistic 
elements, however, it could be easily done by copy/pasting out of a web 
browser into a text editor. 

This program was created as a fun coding project and because it is much 
nicer to enjoy these stories on the reading device of our choosing rather 
than page-by-page in a web browser.

Enjoy.

	INSTALLING / RUNNING THE PROGRAM
	--------------------------------

1) Navigate your command line to the same directory where lit-dl.py is located 
   and run it with: 'python3 lit-dl.py'
2) Make a selection from the main menu
3) Paste literotica.com URLs and let the lit-dl do the rest
4) Stories will be exported in HTML format to the same directory as lit-dl.py
			
	LICENSE INFORMATION
	-------------------

GNU GPLv3.0-or-later

Literotica Downloader (lit-dl) is a program for downloading stories 
from Literotica.

Copyright (C) 2023 NocturnalNebula <nocturnalnebula@proton.me>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

			)
			back_to_menu()
		
		if action == '6':
			exit()
			
# finally, start program here
main_menu()
