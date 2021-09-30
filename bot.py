import telebot
from telebot import types
from course import Course
import time
import os
import sys
import logging
import pickle
import feedparser
import pprint

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
TOKEN = os.environ['LECTURE_BOT_TOKEN']
print(TOKEN)

bot = telebot.TeleBot(token=TOKEN, threaded=False)

default_settings ={}

with open('rss_courses.pkl', 'rb') as inf:
    courses =pickle.load(inf)





