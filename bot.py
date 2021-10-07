from json.encoder import py_encode_basestring_ascii
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


command_to_course = {commandify(c.name+'_'+c.prof):c for d in depts for c in courses[d]}


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
    bot.reply_to(message, f'Welcome! You can use /info to get some help, report a problem, or see the source code. Note that only courses which use the ETH video portal are tracked here.')
    menu(message)


@bot.message_handler(commands=['help', 'Help', 'info', 'Info'])
def help(message):
    chat_id = message.chat.id
    #markup = types.ReplyKeyboardMarkup()
    #btnA = types.KeyboardButton('/Subscribe')
    #btnB = types.KeyboardButton('/Unsubscribe')
    #markup.row(btnA, btnB)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Subscribe', callback_data='sub'), types.InlineKeyboardButton('Unsubscribe', callback_data='unsub'))
    bot.send_message(chat_id, """Note that only courses which use the ETH video portal are tracked here. Use /menu to access the main menu. From there you can choose to /subscribe to a new course, or /unsubscribe from a course you are currently subscribed to.\
 Subscribing to the same course twice will unsubscribe you. 
        
To report a problem send me an email: trevor.winstral@math.ethz.ch
The complete source code is available on Github: https://github.com/TrevorWinstral/ETHLectureBot""",
        disable_web_page_preview=True, reply_markup=markup)



@bot.message_handler(commands=['Menu', 'menu'])
def menu(message, chat_id=None):
    if chat_id: # chat_id=None can leave message blank and just give the chat id to menu()
        chat_id = chat_id
    else:
        chat_id = message.chat.id
    
    try:
        users[chat_id]
    except:
        users[chat_id] = default_settings.copy()
        logger.log(20, msg='Caught user not in dict but in menu')

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Subscribe', callback_data='sub'), types.InlineKeyboardButton('Unsubscribe', callback_data='unsub'))
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
def show_courses_from_dept(message, dept=None):
    chat_id=message.chat.id
    if dept:
        dept=dept
    else:
        dept = message.text[1:].replace('_', '-')
    markup = types.ReplyKeyboardMarkup()
    for course in courses[dept]:
        markup.add(types.KeyboardButton(f"/{commandify(course.name+'_'+course.prof)}"))
    bot.send_message(chat_id, text="Click here -> /menu to return to the main menu\nChoose the course you would like to subscribe to:", reply_markup=markup)


@bot.message_handler(commands=[commandify(c.name+'_'+c.prof) for d in depts for c in courses[d]])
def change_sub_status_to_course(message, course_title=None):
    global users
    chat_id = message.chat.id
    if course_title:
        logger.log(20, f'Received sub/unsub from {chat_id} via course_title: {course_title}')
        text = course_title 
    else:
        logger.log(20, f'Received sub/unsub from {chat_id} via command: {message.text}')
        text = message.text[1:]
    course = command_to_course[text]

    unsubbed = False
    for idx in range(len(course.subscribers)):
        # check if the user was a subscriber to the course, if so we need to remove them as a subscriber from the course
        if chat_id == course.subscribers[idx]:
            logger.log(20, f'User {chat_id} is a sub to course {course.name}, unsubbing')
            del course.subscribers[idx]
            unsubbed = True
    # if we didn't unsub them, they weren't subbed, so now we should sub them to the course    
    if not unsubbed:
        logger.log(20, f'User {chat_id} was not subbed, subbing them to course {course.name}')
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
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Undo this action', callback_data='#SubTo'+text))
        markup.add(types.InlineKeyboardButton('Sub to a course', callback_data='sub'), types.InlineKeyboardButton('Unsub from a course', callback_data='unsub') )
        bot.send_message(chat_id, text=f'You have unsubscribed from the course {course.name} by {course.prof}, VVZ number: {course.code}', reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Undo this action', callback_data='#UnsubFrom'+text))
        markup.add(types.InlineKeyboardButton('Sub to a course', callback_data='sub'), types.InlineKeyboardButton('Unsub from a course', callback_data='unsub') )
        bot.send_message(chat_id, text=f'You subscribed to the course {course.name} by {course.prof}, VVZ number: {course.code}', reply_markup=markup)

    dump_users(users)



@bot.message_handler(commands=['Unsubscribe', 'unsub', 'Unsub', 'unsubscribe'])
def show_subscriptions(message):
    chat_id = message.chat.id
    global users
    markup = types.ReplyKeyboardMarkup()
    for c in users[chat_id]['subscriptions']:
        markup.add(types.KeyboardButton(f"/{commandify(c.name+'_'+c.prof)}"))
    bot.send_message(chat_id, text="Return to the /menu\nHere are your current subscriptions, choose which you would like to unsubscribe from:", reply_markup=markup)


@bot.message_handler(commands=['stats', 'dump'])
def stats(message):
    chat_id = message.chat.id
    global users
    if chat_id in admins:
        dump_users(users)
        bot.send_message(chat_id, text=f'Dumping to pickle. Total users: {len(users)}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Subscribe', callback_data='sub'), types.InlineKeyboardButton('Unsubscribe', callback_data='unsub'))

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    logger.log(20, f'Raw Callback: {call.data}')
    if call.data == 'sub':
        logger.log(20, f'Received Callback from {call.message.chat.id}: sub')
        show_depts(call.message)
    elif call.data == 'unsub':
        logger.log(20, f'Received Callback from {call.message.chat.id}: unsub')
        show_subscriptions(call.message)
    elif call.data[:10] == '#UnsubFrom':
        logger.log(20, f'Received Callback from {call.message.chat.id}: UnsubFrom {call.data[10:]}')
        change_sub_status_to_course(call.message, course_title=call.data[10:])
    elif call.data[:6] == '#SubTo':
        logger.log(20, f'Received Callback from {call.message.chat.id}: SubTo {call.data[6:]}')
        change_sub_status_to_course(call.message, course_title=call.data[6:])


logger.log(20, 'Sending out notifications')
for dept in courses.keys():
    for c in courses[dept]:
        if c.has_been_updated:
            c_text = commandify(c.name+'_'+c.prof)
            logger.log(20, f"Sending notifications for course c_text: {c_text}")
            for sub in c.subscribers:
                try:
                    #markup = types.ReplyKeyboardMarkup()
                    #btnA = types.KeyboardButton('/Subscribe')
                    #btnB = types.KeyboardButton('/Unsubscribe')
                    #markup.row(btnA, btnB)
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Unsub from this course', callback_data='#UnsubFrom'+c_text))
                    markup.add(types.InlineKeyboardButton('Sub to a course', callback_data='sub'), types.InlineKeyboardButton('Unsub from a course', callback_data='unsub') )
                    logger.log(20, str(markup))
                    bot.send_message(sub, f"The course {c.name} has been updated! Check out {c.course_url}\nUse /help for help or to report a problem.", reply_markup=markup)
                    c.has_been_updated = False # this should work as classes are mutable, may be I am wrong though
                    # has_been_updated gets set to false if just 1 person successfully gets updated, no way to notify people who got an error before
                    logger.log(20, f'Nofified the user {sub} an update for their course {c.name}: {c.code}')
                except Exception as e:
                    logger.log(20, f'Something went wrong when trying to send the user {sub} an update for their course {c.name}: {c.code}. Error: {e}')

      
c = courses['d-math'][0]
c_text = commandify(c.name+'_'+c.prof)
markup1 = types.InlineKeyboardMarkup()
markup1.add(types.InlineKeyboardButton('Unsub from this course', callback_data='#UnsubFrom'+c_text))
logger.log(20, '#UnsubFrom'+c_text)
markup1.add(types.InlineKeyboardButton('Sub to a course', callback_data='sub'), types.InlineKeyboardButton('Unsub from a course', callback_data='unsub') )

markup = types.InlineKeyboardMarkup()
markup.add(types.InlineKeyboardButton('Unsub from this course', callback_data='#UnsubFrom'+c_text))
markup.add(types.InlineKeyboardButton('Sub to a course', callback_data='sub'), types.InlineKeyboardButton('Unsub from a course', callback_data='unsub') )
bot.send_message(admins[0], f"The course {c.name} has been updated! Check out {c.course_url}\nUse /help for help or to report a problem.", reply_markup=markup1)



with open('rss_courses.pkl', 'wb') as outf:
    pickle.dump(courses, outf)


while True:
    try:
        bot.polling(none_stop=False, interval=0, timeout=5)
    except Exception as e:
        print(e)
        bot.stop_polling()
        time.sleep(5)