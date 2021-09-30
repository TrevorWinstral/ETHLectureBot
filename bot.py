import telebot
from telebot import types
from course import Course
import re
import time
import os
import sys
import logging
import pickle
import pprint

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
TOKEN = os.environ['LECTURE_BOT_TOKEN']
print(TOKEN)

default_settings ={'subscriptions':[]}

with open('rss_courses.pkl', 'rb') as inf:
    courses =pickle.load(inf)
depts = list(courses.keys())

with open('user_settings.pkl', 'rb') as inf:
    users = pickle.load(inf)

print(depts, users)
def commandify(cmd):
    cmd = cmd.replace(' ', '_')
    cmd = re.sub(r'[^a-zA-Z0-9_À-ÿ]', '', cmd)
    return cmd


command_to_course = {commandify(c.name):c for d in depts for c in courses[d]}


# ============= BOT ===============
bot = telebot.TeleBot(token=TOKEN, threaded=False)
print([d.replace('-', '_') for d in depts])

@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    global users
    chat_id = message.chat.id
    #markup = types.ReplyKeyboardRemove(selective=False)
    try:
        users[message.chat.id]
    except:
        users[message.chat.id] = default_settings.copy()
        logger.log(20, msg='New User!')
    bot.reply_to(message, f'Welcome!')


@bot.message_handler(commands=['Menu', 'menu'])
def menu(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup()
    btnA = types.KeyboardButton('/Subscribe')
    btnB = types.KeyboardButton('/Unsubscribe')
    markup.row(btnA, btnB)
    bot.send_message(chat_id, text ='Here you can choose to subscribe or unsubscribe to a course:', reply_markup=markup)


@bot.message_handler(commands=['Subscribe', 'sub', 'subscribe', 'Sub'])
def show_depts(message):
    chat_id = message.chat.id 
    markup = types.ReplyKeyboardMarkup()
    for dept in depts:
        markup.add(types.KeyboardButton(f"/{dept.replace('-','_')}"))

    bot.send_message(chat_id, text="Choose a Department:",
                     reply_markup=markup)


@bot.message_handler(commands=[d.replace('-', '_') for d in depts])
def show_courses_from_dept(message):
    chat_id=message.chat.id
    dept = message.text[1:].replace('_', '-')
    markup = types.ReplyKeyboardMarkup()
    for course in courses[dept]:
        print(course.name)
        markup.add(types.KeyboardButton(f"/{commandify(course.name)}"))
    bot.send_message(chat_id, text="Choose the course:", reply_markup=markup)


@bot.message_handler(commands=[commandify(c.name) for d in depts for c in courses[d]])
def change_sub_status_to_course(message):
    global users
    chat_id = message.chat.id
    course = command_to_course[message.text[1:]]

    unsubbed = False
    for idx in range(len(course.subscribers)):
        # check if the user was a subscriber to the course, if so we need to remove them as a subscriber from the course
        if chat_id == course.subscribers[idx]:
            del course.subscribers[idx]
            unsubbed = True
    # if we didn't unsub them, they weren't subbed, so now we should sub them to the course    
    if not unsubbed:
        course.subscribers.append(chat_id)
        users[chat_id]['subscriptions'].append(course)
    # if we did unsub them, we need to remove the course from their subscriptions
    else:
        for idx in range(len(users[chat_id]['subscriptions'])):
            if users[chat_id]['subscriptions'][idx].code == course.code:
                del users[chat_id]['subscriptions'][idx]

    # dump user settings and courses to pickle
    with open('user_settings.pkl', 'wb') as outf:
        pickle.dump(users, outf)
    with open('rss_courses.pkl', 'wb') as outf:
        pickle.dump(courses, outf)

    if unsubbed:
        bot.send_message(chat_id, text='You have unsubscribed from the course {course.name} by {course.prof}, VVZ number: {course.code}')
    else:
        bot.send_message(chat_id, text='You subscribed to the course {course.name} by {course.prof}, VVZ number: {course.code}')

@bot.message_handler(commands=['Unsubscribe', 'unsub', 'Unsub', 'unsubscribe'])
def show_subscriptions(message):
    chat_id = message.chat.id
    global users
    markup = types.ReplyKeyboardMarkup()
    for c in users[chat_id]['subscriptions']:
        markup.add(types.KeyboardButton(f"/{commandify(c.name)}"))
    bot.send_message(chat_id, text="Here are your current subscriptions, choose which you would like to unsubscribe from:", reply_markup=markup)


while True:
    try:
        bot.polling(none_stop=False, interval=0, timeout=5)
    except Exception as e:
        print(e)
        bot.stop_polling()
        time.sleep(5)