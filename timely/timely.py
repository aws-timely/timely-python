# -*- coding: utf-8 -*-
import boto.ec2
import sys

from datetime import datetime


class Timely(object):
    def __init__(self, region='us-east-1', iso=False):
        self.conn = boto.ec2.connect_to_region(region)
        self.iso = iso
        # Accommodate for ISO weekday - remove first element if `iso` is False
        weekdays = [
            None,
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday',
        ]
        if iso:
            self.weekdays = weekdays
        else:
            # Remove first element in `weekdays` list object
            weekdays.pop(0)
            self.weekdays = weekdays

    def all(self, instance_ids=None):
        """Read weekday run times for all or specific EC2 instances.

        Args:
            instance_ids (Optional[str]): A list of strings of instance
                IDs
        """
        data = {}
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            times = instance.tags.get('times')
            if times:
                data[instance.id] = []
                times = times.split(';')
                for i in xrange(len(times)):
                    try:
                        start_time, end_time = times[i].split('-')
                        start_time = datetime.strptime(start_time, '%H:%M')
                        end_time = datetime.strptime(end_time, '%H:%M')
                    except ValueError:
                        continue
                    start_time = start_time.strftime('%H:%M')
                    end_time = end_time.strftime('%H:%M')
                    weekday = (self.weekdays[i + 1]
                               if self.iso else self.weekdays[i])
                    data[instance.id].append((weekday, start_time, end_time,))
        return data

    def add(self, instance_ids=None, weekdays=None, start_time=None,
            end_time=None):
        """Create or update weekday run times for all or specific EC2
        instances.

        Args:
            instance_ids (Optional[str]): A list of strings of instance
                IDs
            weekdays (Optional[str]): A list of weekdays
                (e.g. `Monday` - `Sunday`)
            start_time (Optional[str]): The instance starting time
            end_time (Optional[str]): The instance ending time
        """
        ftime = '%H:%M'
        if start_time and end_time:
            start_time = datetime.strptime(start_time,
                                           '%I:%M %p').strftime(ftime)
            end_time = datetime.strptime(end_time, '%I:%M %p').strftime(ftime)
            updated = '{0}-{1}'.format(start_time, end_time)
        else:
            updated = None
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        # integer representation of `weekdays`
        if weekdays == ['*']:
            # All 7 days
            weekdays = range(len(self.weekdays))
        else:
            weekdays = [self.weekdays.index(weekday) for weekday in weekdays]
        for instance in instances:
            if instance.state == 'terminated':
                # Do not tag a terminated instance
                continue
            times = instance.tags.get('times')
            if not times:
                res = raw_input(
                    instance.id + ' ' +
                    'times does not exist. Create default values? [Y/n] '
                )
                if res.lower() == 'y':
                    # No `times` tag - set default
                    times = ';'.join([str(None)] * 7)
                    instance.add_tag('times', times)
                else:
                    continue
            times = times.split(';')
            if self.iso:
                # Need to take into consideration that the user may pass the
                # `iso` argument as True when instantiating the `Timely` class
                times.insert(0, None)
            for weekday in weekdays:
                try:
                    # `weekday` already exists - perform in-place operation
                    times[weekday] = updated
                except IndexError:
                    # If the actual weekday index does not exist, create
                    # default time tags set to `None` until the desired index
                    # is met
                    actual = len(times)
                    desired = weekday
                    while actual < desired:
                        times.append(None)
                        actual += 1
                    # Finally, append the `updated` weekday
                    times.append(updated)
            if self.iso:
                # Remove first element `None` from `times` object
                times.pop(0)
            times = ';'.join([str(time) for time in times])
            try:
                # Overwrite existing `times` tag with new value
                instance.add_tag('times', times)
            except self.conn.ResponseError, e:
                raise e

    def check(self, instance_ids=None):
        """Check the state of instances and either start or stop them
        based on the current time restrictions set for the current day.

        Args:
            instance_ids (Optional[str]): A list of strings of instance
                IDs
        """
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            now = datetime.now()
            if self.iso:
                weekday = now.isoweekday()
            else:
                weekday = now.weekday()
            current = {
                'year': now.year,
                'month': now.month,
                'day': now.day,
            }
            times = instance.tags.get('times')
            if times:
                times = times.split(';')
                try:
                    today = times[weekday]
                except IndexError:
                    continue
                # If instance time is not `None`, cast the `start_time` and
                # `end_time` as `datetime` objects
                if today != 'None':
                    try:
                        start_time, end_time = today.split('-')
                        start_time = datetime.strptime(start_time, '%H:%M')
                        end_time = datetime.strptime(end_time, '%H:%M')
                    except ValueError:
                        continue
                    start_time = start_time.replace(**current)
                    end_time = end_time.replace(**current)
                    if start_time <= now <= end_time:
                        if instance.state == 'stopped':
                            sys.stdout.write(
                                'Starting instance: {0}\r\n'.format(
                                    instance.id
                                )
                            )
                            instance.start()
                    else:
                        if instance.state == 'running':
                            sys.stdout.write(
                                'Stopping instance: {0}\r\n'.format(
                                    instance.id
                                )
                            )
                            instance.stop()
                else:
                    # If the time is `None` check to see if the instance is
                    # running - if it is, then stop it by default
                    if instance.state == 'running':
                        sys.stdout.write(
                            'Stopping instance: {0}\r\n'.format(
                                instance.id
                            )
                        )
                        instance.stop()

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.conn.region.name)

    def __repr__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.conn.region.name)
