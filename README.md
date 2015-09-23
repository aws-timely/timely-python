# timely

timely 0.0.1

Released: 2-Sep-2015

[![Build Status](https://travis-ci.org/rightlag/timely.svg?branch=master)](https://travis-ci.org/rightlag/timely)

---

# Introduction

timely is a Python package that allows users to manage the uptime of their [Amazon Web Services](https://aws.amazon.com/) EC2 containers by providing times at which the containers should be running for any day of the week.

# Requirements

timely requires an `AWS_ACCESS_KEY_ID` and an `AWS_SECRET_ACCESS_KEY`. These can be configured by either exporting [environment variables](https://github.com/boto/boto#getting-started-with-boto) or creating a `~/.boto` [configuration file](https://boto.readthedocs.org/en/latest/getting_started.html#configuring-boto-credentials).

All commits are tested with [Travis CI](https://travis-ci.org/) and *also* require the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables to be set.

# Code Samples

### Fetch all containers and their times

    >>> from timely import Timely
    >>> timely = Timely()
    >>> timely.all()
    {u'i-6dc5bc92': [Time(weekday='Monday', start_time='09:00', end_time='17:00'), Time(weekday='Tuesday', start_time='09:00', end_time='17:00'), Time(weekday='Wednesday', start_time='09:00', end_time='17:00'), Time(weekday='Thursday', start_time='09:00', end_time='17:00'), Time(weekday='Friday', start_time='09:00', end_time='17:00'), Time(weekday='Saturday', start_time='09:00', end_time='17:00'), Time(weekday='Sunday', start_time='09:00', end_time='17:00')]}

### Set times for all containers during certain days of the week

    >>> from timely import Timely
    >>> timely = Timely()
    >>> timely.set(weekdays=['Monday', 'Tuesday', 'Wednesday'], start_time='9:00 AM', end_time='5:00 PM')

### Check if containers should be running

    >>> from timely import Timely
    >>> timely = Timely(verbose=True)
    >>> timely.check()
    Stopping instance: i-6dc5bc92
