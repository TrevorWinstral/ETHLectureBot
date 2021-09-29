''''
Script to find all of the course codes, then find which ones have video RSS feeds.
The source of Courses.pdf should be the list of all courses (not catalogue data) from VVZ
http://vvz.ethz.ch/Vorlesungsverzeichnis/gesamtverzeichnis.view?lang=en
If the courses pdf has been parsed, then READ_PDF can be set to False.
To find which ones have an RSS feed, set FIND_HITS to True.
The URL should be adjusted to reflect the current year / semester, this should be taken care of by year and season variables below
'''

import PyPDF2 
import re, pickle
import feedparser

READ_PDF = False
FIND_HITS = True
Depts = ['d-arch', 'd-baug', 'd-biol', 'd-bsse', 'd-chab', 'd-erdw', 'd-gess', 'd-hest', 'd-infk', 'd-itet', 'd-math', 'd-matl', 'd-mavt', 'd-mtec', 'd-phys', 'd-usys']
year='2021'
season='autumn' #'spring'


if READ_PDF:
    pdffile = open('Courses.pdf', 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdffile)
    txt=pdfReader.getPage(pdfReader.numPages-1).extractText()


    courses=[]
    for page in range(pdfReader.numPages):
        txt = pdfReader.getPage(page).extractText()
        l=re.findall("[0-9]{3}-[0-9]{4}-[0-9A-Z]{3}", txt)
        courses += l
        print(l)

    print(courses)
    pdffile.close()

    courses = list(set(courses))

    with open('all_courses.pkl', 'wb') as infile:
        pickle.dump(courses, infile)
    # regex [0-9]{3}-[0-9]{4}-[0-9A-Z]{3}

if FIND_HITS:

    with open('all_courses.pkl', 'rb') as infile:
        courses= pickle.load(infile)
    print(len(courses))

    hits = []
    for idx in courses:
        for dept in Depts:
            r=feedparser.parse(f'https://video.ethz.ch/lectures/{dept}/{year}/{season}/{idx}.rss.xml?quality=HIGH')
            entries= r.entries
            if entries != []:
                hits.append(idx)
                print(idx, entries[0]['subtitle'])
                break

    with open('rss_courses.pkl', 'wb') as outfile:
        pickle.dump(hits, outfile)