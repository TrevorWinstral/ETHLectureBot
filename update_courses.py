from course import Course
import pickle, feedparser

with open('rss_courses.pkl', 'rb') as inf:
    courses = pickle.load(inf) # just the course code, not the class


for dept in courses.keys():
    for idx in range(len(courses[dept])):
        c = courses[dept][idx]
        c2 = Course(c.dept, c.code, c.year, c.season)
        if c.latest < c2.latest:
            print(f'Updating Course: {c.name}, Code: {c.code}, from {c.latest}, {c.link_to_video} to {c2.latest}, {c2.link_to_video}')
            # This could go wrong if there is some tomfoolery here with the way copying and variable assignment works, not sure. Only one way to find out, deploy!
            c2.has_been_updated = True
            courses[dept][idx] = c2


