# ETH Lecture Bot
Uses RSS feed to send updates via Telegram chatbot when lectures have been uploaded.

## Scripts
`bot.py`: Runs the chatbot

`course.py`: For the course class

`parse_courses.py`: Reads the courses for a given semester, find which have an RSS feed, pickles results

`update_coures.py`: Reads RSS feeds to check when a course has been updated


## Usage
For each new semester, the parse courses script should be ran. This requires the entire course catalogue (the pdf found [here](http://vvz.ethz.ch/Vorlesungsverzeichnis/gesamtverzeichnis.view?lang=en), not the course data file). Further instructions can be found in the script itself. The parameters (below imports) are important; the `year` (YYYY) and `season` (autumn/spring) must be set. If the pdf should be parsed (if you haven't already) `READ_PDF` should be set to `True`, should the courses be filtered out for which an RSS feed does not exist `FIND_HITS` should be set to `True` as well. The full list of courses is saved in the `all_courses.pkl`, and only the courses with RSS feeds are saved in the `rss_courses.pkl`. The `rss_courses.pkl` pickle is a dictionary with the departments as keys corresponding to a list of Course objects.

The `update_courses.py` script should be run at whatever interval is desired. Runtime is the only limiting factor. Script imports all of the admissable courses (those with an RSS feed), then it goes and checks if there is a newer entry in the RSS feed. If there is it updates the lastest item in the respective course class, and sets `has_been_updated` to `True`. After updating, it checks to make sure that it isn't overwriting any changes to the subscribers by importing the latest version of the courses (could have been updated during runtime), it then merges any changes (updates subscribers as well as latest item), and then sends this updated and merged list of courses back to a pickle.

`bot.py` should be run constantly (or whenever you want the bot to work). Very simply interface, the user can either sub to a lecture, or unsub from one they have already subbed to. It is important that when subbing/unsubbing, not only are the user's subscriptions updated, but the course's subscribers as well. When these are changed, the pickle is updated. At a regular time interval the courses are looked through to see if any of them have the `has_been_updated` value been set to `True` in which case, a message is sent to all of the subscribers of that course with the latest lecture information, and this value is then set to `False`. After checking all courses, the pickle is updated.

The notifications are sent out by restarting the bot every 15 minutes (cron job), the updater is called 4 minutes before each bot restart. The bot is currently hosted on my home server.


## TODO

- ~Sort courses into their respective departments (Try to do this programatically)~
    - Each course code seems to have info about department in the first 3 digits (eg. all Math dept courses start with 401-), try to figure this out to prevent need of brute force. Otherwise, query VVZ to figure it out?
    - Solving this by saving which department gave a successful hits when checking which courses have RSS feeds. rss_courses.pkl is now a dict with each dept as a key, for a list of course numbers which fall under that dept. This should be helpful for later when building UI.
- ~Create objects for courses (class) and users (dict)~
- ~Create script to check when a new video has been added, then mark this course to have notification sent out~
- ~Create bot to allow users to change settings, and which regularly checks the courses which are marked for notification and notifies subscribers~
    - partially done, features thus far need to be tested. need to add feature which sends new lecture notifications and properly updates the courses after notifications have been sent.
- ~Make sure that users updating their subscriptions does not get overwritten by courses getting updated~
    - Have `update_courses` read user_settings pickle after it has retrieved everything, making sure each person is still subscribed, maybe have to check that runtime isn't too long with that.