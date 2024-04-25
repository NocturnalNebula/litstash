
        LITSTASH  --  readMe
        --------------------------
        Created by NocturnalNebula
        nocturnalnebula@proton.me
        January 2023
        --------------------------
        GNU GPLv3.0


DESCRIPTION
'''''''''''

This python script can download submissions from Literotica and stories from
xnxx. It also supports Wayback Machine captures from either site. Submissions 
are saved in HTML format with embedded images, audios, and style tags preserved. 

Additionally, litstash can download batches of submissions from series pages, 
search results, or any other page containing submission URLs. Unfortunately,
author pages are not supported, neither 'Works' nor 'Favorites', because
submission URLs are not hardcoded into the page source.

Outputs include story metadata (author, series, date, etc...) for easy
organization or conversion to EPUB in an ebook manager such as Calibre.

REQUIREMENTS
''''''''''''

- git
- Python (version 3.6 or later) 
- the following Python modules: urllib.request, urllib.error, os, sys, 
                                time, json, traceback

All the modules are from the standard library and should be installed 
automatically with Python. Ensure that Python is installed to your PATH and 
check it's version with:

> python --version

OR

> python3 --version

INSTRUCTIONS FOR BASIC USAGE (Mac, Windows, Linux)
''''''''''''''''''''''''''''''''''''''''''''''''''

In a terminal, clone the repository, enter it and run the script with:

> git clone https://github.com/NocturnalNebula/litstash
> cd litstash
> python litstash.py "URLs..."

You may need to type 'python3' instead of 'python' if you have multiple 
versions of Python installed. Literotica URLs should be surrounded by 
"quotes" because an '&' can confuse the shell. You can include multiple 
URLs. URLs can be any Literotica submission or xnxx stories, any page containing
links to either of the above (e.g. author pages), or Wayback Machine captures 
of any of the above. Submissions will be exported to 
".../litstash-saves/username/___.html".

EXAMPLE COMMANDS:

> python litstash.py --version
> python litstash.py --help
> python litstash.py https://www.literotica.com/s/your-smutty-story-34 https://www.literotica.com/p/a-poem-11
> python litstash.py https://www.literotica.com/series/se/00000
> python litstash.py "https://web.archive.org/web/20130919123456/https://www.literotica.com/s/a-deleted-story-4"
> python litstash.py "https://web.archive.org/web/20130723123456/https://www.literotica.com/stories/memberpage.php?uid=0000000&page=submissions"

INSTRUCTIONS FOR INSTALLATION TO PATH (Mac and Linux)
'''''''''''''''''''''''''''''''''''''''''''''''''''''

Install the script to your PATH to be able to call it from anywhere with:
> litstash "URLs..."

1) rename litstash.py to litstash (removing the .py file extension)
> mv litstash.py litstash

2) make it executable
> sudo chmod +x litstash

You can also right-click on the file and choose 'Properties' or 'Get Info' and tick
a box to allow it to execute or 'Run as a program'.

3) move it into your PATH
> sudo mv litstash /usr/local/bin

4) from any directory, test that it is installed
> litstash --version

5) now use it with
> litstash "URL"

LINUX SPECIFIC INSTALL (binary file)
''''''''''''''''''''''''''''''''''''
The linux-bin file is an executable Linux binary of litstash which can be used 
without invoking Python. 

Click on the latest release on the right side of the github page.
There will be a litstash-linux-bin file.

1) save and rename it to remove the -linux-bin part
> mv litstash-linux-bin litstash

2) ensure it is executable
> sudo chmod +x litstash

3) move it to /usr/local/bin
> sudo mv litstash /usr/local/bin

4) from anywhere, test that it is installed with
> litstash --version

5) now use it with
> litstash "URL"

TROUBLESHOOTING
'''''''''''''''

* Did you put quotes around URLs? URLs with '&'s in them require quotes.

* Is the latest version of Python installed?

* Are you using the latest version of litstash?

* If you have multiple versions of Python installed on your system, use:
> python3 litstash.py --help

* Are all the required modules installed? (they should come with Python)

* Are you in the directory containing litstash.py?
In a terminal or command prompt, us the 'cd' command to change directories.

* (Mac or Linux) Try making litstash.py executable with:
> sudo chmod +x litstash.py

* Seeing an error that looks like:
'urllib.error.URLError: <urlopen error unknown url type: https>'?
All requests are made over https so your Python version must be configured 
to use SSL. Try installing the package ndg-httpsclient and check that your 
TLS version is at least 1.3.

* Downloading very slowly?
It is normal for audio files to download slowly from Literotica.com. It is 
also normal for the Wayback Machine to be slow during high-traffic hours. If 
the connection times out or is reset, it will retry in 5 seconds.

* Downloading from the Wayback Machine and getting errors?
Try a different capture of the same submission. If batch downloading many 
submissions, some may create errors and be skipped. Look for a different 
capture for those submissions.

* Are you using many arguments? 
Your OS will have a limit. Try using less arguments.

* Some other bug/error?
I intend to continue supporting and improving this software. Therefore, 
report any bugs on the github page or by email. Include a description of the 
problem and any links to submissions that created errors. Don't be shy; I 
don't care what kind of smut you're into.

A NOTE ON WAYBACK MACHINE CAPTURES
''''''''''''''''''''''''''''''''''

Literotica has changed its site scheme/format four times since its inception. 
Each change was relevant to how the submission data is scraped from the source 
HTML. While downloading from Wayback Machine captures, you'll notice that the 
scheme of each page is displayed. Although I have done everything I can to 
fully support all types of submissions from all site schemes, you may find 
occasional bugs, especially with older schemes. The scheme with the strongest 
support is probably Classic (2014-2021/04).

The names that I've given to each scheme along with their approximate dates 
are given below.

Original      -  1999-2009
Post-Original -  2009-2012
Pre-Classic   -  2012-2014
Classic       -  2014-2021/04
Modern        -  2021/04-present

COMMENTS, BUGS, QUESTIONS?
''''''''''''''''''''''''''

Send me an email. I am happy to get your comments and to help to get litstash
working for you.

nocturnalnebula@proton.me
