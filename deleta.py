
year, week = datetime.datetime.now().isocalendar()[0:2]
date = datetime.date(year, 1, 1)
if (date.weekday() > 3):
    date = date + datetime.timedelta(7 - date.weekday())
else:
    date = date - datetime.timedelta(date.weekday())
delta = datetime.timedelta(days=(week - 1) * 7)
start, end = date + delta, date + delta + datetime.timedelta(days=6)
print(start)
print(end)