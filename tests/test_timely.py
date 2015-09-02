import boto.ec2
import datetime
import unittest

from timely import Timely


class TimelyTestCase(unittest.TestCase):
    def setUp(self):
        self.timely = Timely()
        self.conn = boto.ec2.connect_to_region('us-east-1')
        self.now = datetime.datetime.now()

    def test_times_tag_is_created(self):
        self.timely.add(weekdays=['*'])
        instances = self.conn.get_only_instances()
        for instance in instances:
            if instance.state != 'terminated':
                self.assertIn('times', instance.tags)
            else:
                continue

    def test_times_tag_has_length_of_7(self):
        instances = self.conn.get_only_instances()
        for instance in instances:
            # Ensure that the length of the `times` list object has a length
            # of 7
            times = instance.tags['times'].split(';')
            self.assertEqual(len(times), 7)

    def test_time_is_set_for_weekday(self):
        weekday = self.timely.weekdays[self.now.weekday()]
        start_time = self.now - datetime.timedelta(hours=1)
        end_time = self.now + datetime.timedelta(hours=1)
        start_time = start_time.strftime('%I:%M %p')
        end_time = end_time.strftime('%I:%M %p')
        self.timely.add(weekdays=[weekday], start_time=start_time,
                        end_time=end_time)
        instances = self.conn.get_only_instances()
        for instance in instances:
            times = instance.tags['times'].split(';')
            self.assertNotEqual(times[self.now.weekday()], str(None))

    def test_ensure_instance_is_running(self):
        self.timely.check()
        instances = self.conn.get_only_instances()
        for instance in instances:
            if instance.state != 'terminated':
                self.assertEqual(instance.state, 'running')
            else:
                continue

    def tearDown(self):
        del self.timely
