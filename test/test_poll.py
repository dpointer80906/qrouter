"""Poll unittest module.

"""
import unittest
import poll

# TODO figure out a way to test the argparse type checkers, the argparse.ArgumentTypeError exception breaks things


class TestPoll(unittest.TestCase):
    """Poll file functions unit tests.

    """

    def setUp(self):
        print('\n***** executing {}'.format(self._testMethodName))
        self.args = poll.parse_args()

    def test_default_parse_args(self):
        """Check for correct default arguments."""
        self.assertEqual(self.args.router, poll.DEFAULT_ROUTER)
        self.assertEqual(self.args.port, poll.DEFAULT_PORT)
        self.assertEqual(self.args.interval, poll.DEFAULT_INTERVAL)
        self.assertEqual(self.args.community, poll.DEFAULT_COMMUNITY)
        self.assertEqual(self.args.iterations, poll.DEFAULT_ITERATIONS)

    def test_poll(self):
        """Run poll() with default arguments."""
        ret = poll.poll(self.args)
        self.assertEqual(ret, poll.NOERROR)


if __name__ == '__main__':
    unittest.main()


# TODO need more unit tests for poll(), refactor poll()?
