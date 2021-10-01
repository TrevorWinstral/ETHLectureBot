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
admins=[995547885]

with open('rss_courses.pkl', 'rb') as inf:
    courses =pickle.load(inf)
depts = list(courses.keys())

with open('user_settings.pkl', 'rb') as inf:
    users = pickle.load(inf)


def commandify(cmd):
    cmd = cmd.replace(' ', '_')
    cmd = re.sub(r'[^a-zA-Z0-9_À-ÿ]', '', cmd)
    return cmd

def dump_users(users):
    with open('user_settings.pkl', 'wb') as outf:
        pickle.dump(users, outf)


command_to_course = {commandify(c.name):c for d in depts for c in courses[d]}


# ============= BOT ===============
bot = telebot.TeleBot(token=TOKEN, threaded=False)

@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    global users
    try:
        users[message.chat.id]
    except:
        users[message.chat.id] = default_settings.copy()
        logger.log(20, msg='New User!')

    dump_users(users)
    bot.reply_to(message, f'Welcome! You can use /info to get some help, report a problem, or see the source code')
    menu(message)


@bot.message_handler(commands=['help', 'Help', 'info', 'Info'])
def help(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, """Use /menu to access the main menu. From there you can choose to /subscribe to a new course, or /unsubscribe from a course you are currently subscribed to.\
Subscribing to the same course twice will unsubscribe you. 
        
To report a problem send me an email: trevor.winstral@math.ethz.ch
The complete source code is available on Github: https://github.com/TrevorWinstral/ETHLectureBot""",
        disable_web_page_preview=True)
    menu(message)


@bot.message_handler(commands=['Menu', 'menu'])
def menu(message, chat_id=None):
    chat_id = message.chat.id
    if not chat_id: # w, chat_id=Nonee can leave message blank and just give the chat id to menu()
        chat_id = message.chat.id
    try:
        users[message.chat.id]
    except:
        users[message.chat.id] = default_settings.copy()
        logger.log(20, msg='Caught user not in dict but in menu')

    markup = types.ReplyKeyboardMarkup()
    btnA = types.KeyboardButton('/Subscribe')
    btnB = types.KeyboardButton('/Unsubscribe')
    markup.row(btnA, btnB)
    bot.send_message(chat_id, text ='You can always use /menu to return here, /info for help or more information.\nYou can choose to subscribe or unsubscribe to a course:', reply_markup=markup)


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
        markup.add(types.KeyboardButton(f"/{commandify(course.name)}"))
    bot.send_message(chat_id, text="Return to the /menu\nChoose the course:", reply_markup=markup)


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
        bot.send_message(chat_id, text=f'You have unsubscribed from the course {course.name} by {course.prof}, VVZ number: {course.code}')
    else:
        bot.send_message(chat_id, text=f'You subscribed to the course {course.name} by {course.prof}, VVZ number: {course.code}')

    dump_users(users)
    menu(message)

@bot.message_handler(commands=['Unsubscribe', 'unsub', 'Unsub', 'unsubscribe'])
def show_subscriptions(message):
    chat_id = message.chat.id
    global users
    markup = types.ReplyKeyboardMarkup()
    for c in users[chat_id]['subscriptions']:
        markup.add(types.KeyboardButton(f"/{commandify(c.name)}"))
    bot.send_message(chat_id, text="Return to the /menu\nHere are your current subscriptions, choose which you would like to unsubscribe from:", reply_markup=markup)


@bot.message_handler(commands=['stats', 'dump'])
def stats(message):
    chat_id = message.chat.id
    global users
    if chat_id in admins:
        dump_users(users)
        bot.send_message(chat_id, text=f'Dumping to pickle. Total users: {len(users)}')
        menu()

logger.log(20, 'Sending out notifications')
for dept in courses.keys():
    for c in courses[dept]:
        if c.has_been_updated:
            for sub in c.subscribers:
                try:
                    bot.send_message(sub, f"The course {c.name} has been updated! Check out {c.link_to_video}")
                    menu(None, chat_id=sub)
                except Exception as e:
                    logger.log(20, 'Something went wrong when trying to send the user {sub} an update for their course {c.name}: {c.code}. Error: {e}')

while True:
    try:
        bot.polling(none_stop=False, interval=0, timeout=5)
    except Exception as e:
        print(e)
        bot.stop_polling()
        time.sleep(5)