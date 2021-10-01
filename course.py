import feedparser
import datetime

class Course:
    def __init__(self, dept, code, year, season, subs=[]):
        self.dept = dept
        self.code = code
        self.year = year
        self.season = season
        self.url = f'https://video.ethz.ch/lectures/{dept}/{year}/{season}/{code}.rss.xml?quality=HIGH'
        self.feed = feedparser.parse(self.url)
        self.latest = datetime.datetime.strptime(self.feed.entries[0]['published'],r'%Y-%m-%dT%H:%MZ')
        self.link_to_video = self.feed.entries[0]['link']
        self.name = self.feed.entries[0]['subtitle']
        self.prof = self.feed.entries[0]['author']
        self.has_been_updated = False
        self.subscribers=subs
        self.course_url=f'https://video.ethz.ch/lectures/{dept}/{year}/{season}/{code}.html'