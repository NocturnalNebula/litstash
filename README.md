# lit-dl (Literotica Downloader)

### README
* lit-dl-v1.2
* Compatibility: Windows, Mac, Linux, others
* Created by NocturnalNebula in Jan 2023 <nocturnalnebula@proton.me>
* GNU GPLv3.0-or-later
* Updated: August 2023

---

### DESCRIPTION

Welcome to lit-dl (Literotica Downloader), a tool for downloading stories from Literotica. This program will download stories in HTML format from literotica.com and from the "classic" Literotica format accessed through the Wayback Machine. However, very old Wayback Machine captures from before Literotica's site format change around 2012 will cause lit-dl to crash.

This program was originally written in python3 in January 2023 as an alternative to other Literotica downloaders which stopped working after the site changed its format several years ago.

It is capable of downloading individual stories or batch downloading all the story submissions from a particular user. The exported HTML files retain paragraph, linebreak, bold, italics, and other style tags and look nice on an e-reader. Parsing the HTML to TXT exports would remove these stylistic elements, however, it could be easily done by copy/pasting out of a web browser into a text editor.

This program was created as a fun coding project and because it is much nicer to enjoy these stories on the reading device of our choosing rather than page-by-page in a web browser.

---

### INSTALLING / USING THE PROGRAM

There are two ways to use this program.
1) Simply execute the python3 script in a terminal.
2) On linux, install lit-dl.deb (DEB package containing a binary of the program). See the latest release to find DEB package at https://github.com/NocturnalNebula/lit-dl/releases/.

#### RUNNING THE SCRIPT

1) With python3 installed, navigate your command line to the same directory where lit-dl.py is located and run it with:

>python3 lit-dl.py

Or, if python3 is the only version you have installed:

>python lit-dl.py

2) Make a selection from the main menu.
3) Paste literotica.com URLs and let the lit-dl do the rest.
4) Stories will be exported in HTML format to the current working directory, which can be changed from the main menu.

---

### TROUBLESHOOTING

A few things to fix various problems:
* Ensure that python3 is installed.
* If you are seeing errors about urllib, such as, *NameError: name 'urllib' is not defined*, you might need to install urllib, although this should not be necessary as urllib is a standard library. Try reinstalling python3, and if you have pip installed, use:

> pip install urllib

* It may be necessary that you have execute permissions on lit-dl.py

> sudo chmod +x lit-dl.py

* lit-dl might seem to download very slowly and get stuck on various steps  (especially from the Wayback Machine) because it needs to scrape source data from the website. Just wait. If it gets a timeout error, it will tell you and retry three times.
