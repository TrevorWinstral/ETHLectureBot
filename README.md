# ETH Lecture Bot
Uses RSS feed to send updates via Telegram chatbot when lectures have been uploaded.

## Scripts
`bot.py`: Runs the chatbot
`course.py`: For the course class
`parse_courses.py`: Reads the courses for a given semester, find which have an RSS feed, pickles results
`update_coures.py`: Reads RSS feeds to check when a course has been updated


## Usage
For each new semester, the parse courses script should be ran. This requires the entire course catalogue (the pdf found [here](http://vvz.ethz.ch/Vorlesungsverzeichnis/gesamtverzeichnis.view?lang=en), not the course data file). Further instructions can be found in the script itself. The parameters (below imports) are important; the `year` (YYYY) and `season` (autumn/spring) must be set. If the pdf should be parsed (if you haven't already) `READ_PDF` should be set to `True`, should the courses be filtered out for which an RSS feed does not exist `FIND_HITS` should be set to `True` as well. The full list of courses is saved in the `all_courses.pkl`, and only the courses with RSS feeds are saved in the `rss_courses.pkl`. The `rss_courses.pkl` pickle is a dictionary with the departments as keys corresponding to a list of Course objects.

## TODO

- ~Sort courses into their respective departments (Try to do this programatically)~
    - Each course code seems to have info about department in the first 3 digits (eg. all Math dept courses start with 401-), try to figure this out to prevent need of brute force. Otherwise, query VVZ to figure it out?
    - Solving this by saving which department gave a successful hits when checking which courses have RSS feeds. rss_courses.pkl is now a dict with each dept as a key, for a list of course numbers which fall under that dept. This should be helpful for later when building UI.
- ~Create objects for courses (class) and users (dict)~
- ~Create script to check when a new video has been added, then mark this course to have notification sent out~
- Create bot to allow users to change settings, and which regularly checks the courses which are marked for notification and notifies subscribers