import boto.ec2
import datetime
import pytz
import sys
import unittest

from time import sleep
from timely import Timely


class TimelyTestCase(unittest.TestCase):
    def setUp(self):
        self.timely = Timely(verbose=True)
        self.conn = boto.ec2.connect_to_region('us-east-1')
        self.now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))

    def test_times_tag_is_created(self):
        t1 = datetime.time(9, 0)
        t2 = datetime.time(17, 0)
        self.timely.set(t1, t2)
        instances = self.conn.get_only_instances()
        for instance in instances:
            self.assertIn('times', instance.tags)
            self.assertIn('tz', instance.tags)

    def test_times_tag_has_length_of_7(self):
        t1 = datetime.time(9, 0)
        t2 = datetime.time(17, 0)
        self.timely.set(t1, t2)
        instances = self.conn.get_only_instances()
        for instance in instances:
            # Ensure that the length of the `times` list object has a length
            # of 7
            times = instance.tags['times'].split(';')
            self.assertEqual(len(times), 7)

    def test_time_is_set_for_weekday(self):
        """Assert that a time is set for the current weekday."""
        weekday = self.timely.weekdays[self.now.weekday()]
        t1 = datetime.time(9, 0)
        t2 = datetime.time(17, 0)
        self.timely.set(t1, t2, weekdays=[weekday])
        instances = self.conn.get_only_instances()
        for instance in instances:
            times = instance.tags['times'].split(';')
            self.assertNotEqual(times[self.now.weekday()], str(None))

    def test_exception_if_start_time_is_greater_than_equal_to_end_time(self):
        """If the start time is greater than or equal to the end time
        a `ValueError` should be raised.
        """
        with self.assertRaises(ValueError):
            # Greater
            t1 = datetime.time(9, 0)
            t2 = datetime.time(8, 0)
            self.timely.set(t1, t2)
            # Equal
            t1 = datetime.time(9, 0)
            t2 = datetime.time(9, 0)
            self.timely.set(t1, t2)

    def test_unset_method(self):
        t1 = datetime.time(9, 0)
        t2 = datetime.time(17, 0)
        self.timely.set(t1, t2)
        instances = self.conn.get_only_instances()
        for instance in instances:
            times = instance.tags['times'].split(';')
            self.assertEqual(len(times), 7)
        self.timely.unset()
        for instance in instances:
            instance.update()
            times = instance.tags['times']
            self.assertEqual(times, ';'.join([str(None)] * 7))

    def test_check_method_stops_instance_if_should_not_be_running(self):
        """
        Check to ensure that an instance is stopped if it SHOULD NOT be
        running.
        """
        try:
            instance = self.conn.get_only_instances()[0]
            if instance.state == 'stopped':
                running = False
                # Start the instance to ensure it is running
                sys.stdout.write('starting instance: {0}\n'
                                 .format(instance.id))
                instance.start()
                while not running:
                    instance.update()
                    if instance.state == 'running':
                        running = True
                    else:
                        sleep(1)
            t1 = datetime.time(9, 0)
            t2 = datetime.time(17, 0)
            weekday = self.timely.weekdays[self.now.weekday()]
            # Automatically sets `start_time` and `end_time` to `None`
            self.timely.set(t1, t2, weekdays=[weekday])
            # Ensure that the instance is being stopped
            self.timely.check()
            stopped = False
            while not stopped:
                instance.update()
                if instance.state == 'stopped':
                    stopped = True
                else:
                    sleep(1)
            self.assertEqual(instance.state, 'stopped')
        except IndexError:
            pass

    def tearDown(self):
        del self.timely
