# ETH Lecture Bot
Uses RSS feed to send updates when lectures have been uploaded.


## Usage
For each new semester, the parse courses script should be ran. This requires the entire course catalogue (the pdf found [here](http://vvz.ethz.ch/Vorlesungsverzeichnis/gesamtverzeichnis.view?lang=en), not the course data file). Further instructions can be found in the script itself. The parameters (below imports) are important; the `year` (YYYY) and `season` (autumn/spring) must be set. If the pdf should be parsed (if you haven't already) `READ_PDF` should be set to `True`, should the courses be filtered out for which an RSS feed does not exist `FIND_HITS` should be set to `True` as well. The full list of courses is saved in the `all_courses.pkl`, and only the courses with RSS feeds are saved in the `rss_courses.pkl`.

## TODO
- Sort courses into their respective departments (Try to do this programatically)
    - Each course code seems to have info about department in the first 3 digits (eg. all Math dept courses start with 401-), try to figure this out to prevent need of brute force. Otherwise, query VVZ to figure it out?
- Create objects for courses and users (maybe use dicts and not classes)
- Create script to check when a new video has been added, then mark this course to have notification sent out
- Create bot to allow users to change settings, and which regularly checks the courses which are marked for notification and notifies subscribers