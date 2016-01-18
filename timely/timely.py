import boto.ec2
import collections
import datetime
import pytz
import sys

from datetime import datetime


class Timely(object):
    def __init__(self, region='us-east-1', iso=False, verbose=False,
                 tz='US/Eastern'):
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
        self.verbose = verbose
        self.set_tz(tz)

    def use_verbose(self):
        self.verbose = True

    def use_iso(self):
        self.iso = True

    def set_region(self, region):
        self.conn = boto.ec2.connect_to_region(region)

    def set_tz(self, tz):
        try:
            self.tz = pytz.timezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            self.tz = pytz.utc

    def _verbose_message(self, action, instance):
        sys.stdout.write('{0} instance: {1}\n'.format(action, instance.id))

    def all(self, instance_ids=None, as_dict=False):
        """
        Read weekday run times for all or specific EC2 instances.

        :type instance_ids: list
        :param instance_ids: A list of strings of instance IDs

        :type as_dict: bool
        :param as_dict: Set if data should be returned as a `dict`
            instead of a `namedtuple`
        """
        data = {}
        Time = collections.namedtuple('Time',
                                      ['weekday', 'start_time', 'end_time'])
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            times = instance.tags.get('times')
            if times:
                data[instance.id] = []
                times = times.split(';')
                for i in xrange(len(times)):
                    try:
                        start_time, end_time = times[i].split('-')
                        start_time = datetime.strptime(start_time, '%H:%M:%S')
                        end_time = datetime.strptime(end_time, '%H:%M:%S')
                    except ValueError:
                        continue
                    try:
                        # If `tz` key exists, create `tz` object, otherwise
                        # create default UTC `tz` object
                        tz = instance.tags['tz']
                        tz = pytz.timezone(tz)
                    except KeyError:
                        tz = pytz.utc
                    start_time = tz.localize(start_time).timetz()
                    end_time = tz.localize(end_time).timetz()
                    weekday = (
                        self.weekdays[i + 1] if self.iso else self.weekdays[i]
                    )
                    time = Time(weekday, start_time, end_time)
                    if as_dict:
                        # Ordered dictionary representation of weekday times
                        time = time._asdict()
                    data[instance.id].append(time)
        return data

    def set(self, start_time, end_time, weekdays=None, instance_ids=None):
        """
        Create or update weekday run times for all or specific EC2
        instances.

        :type instance_ids: list
        :param instance_ids: A list of strings of instance IDs

        :type weekdays: list
        :param weekdays: A list of strings of weekdays (e.g. `Monday`)

        :type start_time: datetime.time
        :param start_time: The instance starting time

        :type end_time: datetime.time
        :param end_time: The instance ending time
        """
        if start_time >= end_time:
            raise ValueError(
                'Start time can\'t be greater than or equal to end time'
            )
        start_time = start_time.isoformat()
        end_time = end_time.isoformat()
        updated = '{0}-{1}'.format(start_time, end_time)
        # integer representation of `weekdays`
        if weekdays:
            weekdays = [self.weekdays.index(weekday) for weekday in weekdays]
        else:
            # `weekdays` not set, assign times for entire week
            weekdays = range(len(self.weekdays))
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            if instance.state == 'terminated':
                # Do not tag a terminated instance
                continue
            times = instance.tags.get('times')
            if not times:
                # No `times` tag - set defaults
                times = ';'.join([str(None)] * 7)
                tags = {
                    'times': times,
                    'tz': self.tz,
                }
                try:
                    instance.add_tags(tags)
                except self.conn.ResponseError, e:
                    raise e
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
                    # Append the `updated` weekday
                    times.append(updated)
                finally:
                    # If the length of the `times` list object is less than 7,
                    # then extend the list object to include the remaining
                    # times
                    if len(times) < 7:
                        diff = 7 - len(times)
                        times.extend([None] * diff)
            if self.iso:
                # Remove first element `None` from `times` object
                times.pop(0)
            times = ';'.join([str(time) for time in times])
            tags = {
                'times': times,
                'tz': self.tz,
            }
            try:
                # Overwrite existing `times` tag with new value
                instance.add_tags(tags)
            except self.conn.ResponseError, e:
                raise e

    def unset(self, instance_ids=None, weekdays=None):
        """
        Unset instance times for specific weekdays or all weekdays.

        :type instance_ids: list
        :param instance_ids: A list of strings of instance IDs

        :type weekdays: list
        :param weekdays: A list of strings of weekdays (e.g. `Monday`)
        """
        # integer representation of `weekdays`
        if weekdays:
            weekdays = [self.weekdays.index(weekday) for weekday in weekdays]
        else:
            # `weekdays` not set, assign times for entire week
            weekdays = range(len(self.weekdays))
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            times = instance.tags.get('times')
            if times:
                times = times.split(';')
                for weekday in weekdays:
                    times[weekday] = None
                times = ';'.join([str(time) for time in times])
                try:
                    # Overwrite existing `times` tag with new value
                    instance.add_tag('times', times)
                except self.conn.ResponseError, e:
                    raise e

    def check(self, instance_ids=None):
        """
        Check the state of instances and either start or stop them based
        on the current time restrictions set for the current day.

        :type instance_ids: list
        :param instance_ids: A list of strings of instance IDs
        """
        instances = self.conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            tz = instance.tags.get('tz')
            if not tz:
                # Needs to be a timezone to compare current time to
                # `start_time` and `end_time` - otherwise continue
                continue
            tz = pytz.timezone(tz)
            now = datetime.now(tz=tz)
            if self.iso:
                weekday = now.isoweekday()
            else:
                weekday = now.weekday()
            times = instance.tags.get('times')
            if times:
                times = times.split(';')
                try:
                    today = times[weekday]
                except IndexError:
                    continue
                # If instance time is not `None`, cast the `start_time` and
                # `end_time` as `datetime` objects
                if today != str(None):
                    try:
                        start_time, end_time = today.split('-')
                        start_time = datetime.strptime(start_time, '%H:%M:%S')
                        end_time = datetime.strptime(end_time, '%H:%M:%S')
                    except ValueError:
                        continue
                    start_time = start_time.replace(year=now.year,
                                                    month=now.month,
                                                    day=now.day)
                    end_time = end_time.replace(year=now.year,
                                                month=now.month, day=now.day)
                    # http://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/#add-timezone-localize
                    start_time = tz.localize(start_time)
                    end_time = tz.localize(end_time)
                    if start_time <= now <= end_time:
                        if instance.state == 'stopped':
                            if self.verbose:
                                self._verbose_message('starting', instance)
                            instance.start()
                    else:
                        if instance.state == 'running':
                            if self.verbose:
                                self._verbose_message('stopping', instance)
                            instance.stop()
                else:
                    # If the time is `None` check to see if the instance is
                    # running - if it is, then stop it by default
                    if instance.state == 'running':
                        if self.verbose:
                            self._verbose_message('stopping', instance)
                        instance.stop()

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.conn.region.name)

    def __repr__(self):
        return str(self)
