import telebot
from telebot import types
import time
import os
import sys
import logging
import pickle
import feedparser
import pprint

r=feedparser.parse('https://video.ethz.ch/lectures/d-math/2021/autumn/401-0000-00L.rss.xml?key=b3074a&quality=HIGH')
print(r.entries)


