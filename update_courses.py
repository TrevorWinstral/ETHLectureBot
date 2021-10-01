from course import Course
import pickle, feedparser

with open('rss_courses.pkl', 'rb') as inf:
    courses = pickle.load(inf) 

print('Updating courses')
for dept in list(courses.keys()):
    for idx in range(len(courses[dept])):
        c = courses[dept][idx]
        c2 = Course(c.dept, c.code, c.year, c.season, subs=c.subscribers)
        if c.latest < c2.latest:
            print(f'Updating Course: {c.name}, Code: {c.code}, from {c.latest}, {c.link_to_video} to {c2.latest}, {c2.link_to_video}')
            # This could go wrong if there is some tomfoolery here with the way copying and variable assignment works, not sure. Only one way to find out, deploy!
            c2.has_been_updated = True
            courses[dept][idx] = c2
print('All courses updated, merging subscribers')

with open('rss_courses.pkl', 'rb') as inf:
    courses2 = pickle.load(inf) # this is to used to update the subscriber list of each course, as it could have been modified by users during the runtime of this script

for dept in courses.keys():
    for idx in range(len(courses[dept])):
        # this is redundant, but I can't help to think that somehow the courses may get shuffled, want to avoid that
        if courses[dept][idx].code == courses2[dept][idx].code:
            courses[dept][idx].subscribers = courses2[dept][idx].subscribers

print("Sorting the courses")
for dept in courses.keys():
    courses[dept].sort(key=lambda c: c.name)

print('Merging done, dumping to pickle')
with open('rss_courses.pkl', 'wb') as outf:
    pickle.dump(courses, outf)



# TODO dump to pickle, check that we haven't changed subscriptions somewhere


