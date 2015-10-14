# timely

timely 0.0.2

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
    {u'i-6dc5bc92': [Time(weekday='Monday', start_time=datetime.time(9, 0, tzinfo=<DstTzInfo 'US/Eastern' LMT-1 day, 19:04:00 STD>), end_time=datetime.time(17, 0, tzinfo=<DstTzInfo 'US/Eastern' LMT-1 day, 19:04:00 STD>))]}

### Set times for all containers during certain days of the week

    >>> from timely import Timely
    >>> from datetime import time
    >>> timely = Timely()
    >>> t1 = time(9, 0)
    >>> t2 = time(17, 0)
    >>> timely.set(t1, t2, weekdays=['Monday'])

### Check if containers should be running

    >>> from timely import Timely
    >>> timely = Timely(verbose=True)
    >>> timely.check()
    Stopping instance: i-6dc5bc92

### Using timezones

By default, `timely` sets the default timezone to `US/Eastern`. However, this can be changed upon instantiation of the `timely` class or via the `set_tz` method. For example:

    >>> from timely import Timely
    >>> timely = Timely(tz='US/Pacific')
    >>> timely.set_tz('US/Mountain')

If the timezone specified does not exist, then `UTC` is used.

When assigning the timezone, the `set` method will create a tag `tz` for EC2 containers with the timezone that was specified. Whenever the `check` method is called, the `tz` tag that is assigned to the EC2 container is used to determine whether or not it should be running.
