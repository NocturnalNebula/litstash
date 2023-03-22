# Literotica Downloader (lit-dl)

DESCRIPTION
-----------
Welcome to Literotica Downloader (lit-dl v.1.1), a Python3 tool for downloading stories from Literotica. This command line program will download stories in HTML format from literotica.com and from the "classic" Literotica format accessed through the Wayback Machine. However, very old Wayback Machine captures from before Literotica's site format change around 2012 will cause lit-dl to crash.

This program was written in January 2023 as an alternative to other Literotica downloaders which stopped working after Lit changed the format of the site several years ago. As of the time of this writing, lit-dl works nicely with the current format of Literotica.

It is capable of downloading individual stories or batch downloading all the story submissions from a particular user. The exported HTML files retain paragraph, linebreak, bold, italics, and other style tags and look nice on an e-reader. Parsing the HTML to TXT exports would remove these stylistic elements, however, it could be easily done by copy/pasting out of a web browser into a text editor. 

This program was created as a fun coding project and because it is much nicer to enjoy these stories on the reading device of our choosing rather than page-by-page in a web browser.

Enjoy.

INSTALLING / RUNNING THE PROGRAM
--------------------------------

1) Navigate your command line to the same directory where lit-dl.py is located and run it with: 'python3 lit-dl.py'
2) Make a selection from the main menu
3) Paste literotica.com URLs and let the lit-dl do the rest
4) Stories will be exported in HTML format to the same directory as lit-dl.py

TROUBLESHOOTING
---------------

If the program is not working as expected you should first check a few things.

1) Ensure that python3 is installed

Windows: https://www.python.org/downloads/windows/

MacOS: https://www.python.org/downloads/macos/

Linux (Ubuntu Family): Type "sudo apt-get install python3" into the command line. 

Linux (Other): If you are using non-Ubuntu Linux I think it is safe to assume you can figure out how to install python3 on your own.

2) If you are seeing errors about urllib such as "NameError: name 'urllib' is not defined" you might need to install urllib, although this should not be necessary as urllib is a standard library

Try reinstalling python3 first then try 'pip install urllib' to install urllib. You will probably need to install pip first, as well.

3) It may be necessary that you have execute permissions on lit-dl.py

INFO
----

Created by NocturnalNebula in Jan 2023 : nocturnalnebula@proton.me

GNU GPLv3.0-or-later

Updated: March 2023
