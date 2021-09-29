import telebot
from telebot import types
import time
import os
import sys
import logging
import pickle
import requests
from bs4 import BeautifulSoup
import feedparser
import pprint

r=feedparser.parse('https://video.ethz.ch/lectures/d-math/2021/autumn/401-0000-00L.rss.xml?key=b3074a&quality=HIGH')
print(r.entries)

with open('courses.pkl', 'rb') as infile:
    courses= pickle.load(infile)
print(len(courses))


hits = []
for idx in courses:
    r=feedparser.parse(f'https://video.ethz.ch/lectures/d-math/2021/autumn/{idx}.rss.xml?quality=HIGH')
    entries= r.entries
    if entries != []:
        hits.append(idx)
        print(idx, entries[0]['subtitle'])


print(f'Found {len(hits)} hits')

