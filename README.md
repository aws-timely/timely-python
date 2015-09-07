# timely

timely 0.0.1

Released: 2-Sep-2015

---

# Introduction

timely is a Python package that allows users to manage the uptime of their [Amazon Web Services](https://aws.amazon.com/) EC2 containers by providing times at which the containers should be running for any day of the week.

# Code Samples

### Fetch all containers and their times

    >>> from timely import Timely
    >>> timely = Timely()
    >>> timely.all()
    {u'i-6dc5bc92': [('Monday', '09:00', '17:00'), ('Tuesday', '09:00', '17:00'), ('Wednesday', '09:00', '17:00')]}

### Set times for all containers during certain days of the week

    >>> from timely import Timely
    >>> timely = Timely()
    >>> timely.set(weekdays=['Monday', 'Tuesday', 'Wednesday'], start_time='9:00 AM', end_time='5:00 PM')

### Check if container should be running

    >>> from timely import Timely
    >>> timely = Timely(verbose=True)
    >>> timely.check()
    Stopping instance: i-6dc5bc92
