"""qrouter - poll-query two router interfaces via SNMP,

Print input/output line rates and total byte counts for each interface.
"""
import sys
import argparse
import time
from pysnmp.entity.rfc3413.oneliner import cmdgen

OID_IFINOCTETS = '1.3.6.1.2.1.2.2.1.10'
OID_IFOUTOCTETS = '1.3.6.1.2.1.2.2.1.16'
OID_IFHCINOCTETS = '1.3.6.1.2.1.31.1.1.1.6'
OID_IFHCOUTOCTETS = '1.3.6.1.2.1.31.1.1.1.10'
OID_IF1 = '.1'
OID_IF2 = '.2'

DEFAULT_ROUTER = "demo.snmplabs.com"
DEFAULT_PORT = 1161
DEFAULT_INTERVAL = 1
DEFAULT_COMMUNITY = "public"
DEFAULT_ITERATIONS = 1

ERROR = 1
NOERROR = 0


def check_iterations(value):
    """Check that the argument iterations is 0 or positive integer.

    Args:
        value: the value to check.

    Returns:
        (int) the integer value of the arg "value".

    Raises:
        argparse.ArgumentTypeError if check fails.
    """
    ivalue = int(value)
    if 0 <= ivalue <= sys.maxsize:
        pass
    else:
        msg = "iterations (%s) invalid, must be 0 or positive integer" % value
        raise argparse.ArgumentTypeError(msg)
    return ivalue


def check_interval(value):
    """Check that the argument interval is a positive integer.

    Args:
        value: the value to check.

    Returns:
        (int) the integer value of the arg "value".

    Raises:
        argparse.ArgumentTypeError if check fails.
    """
    ivalue = int(value)
    if ivalue <= 0:
        msg = "interval (%s) invalid, must be 0 or positive integer" % value
        raise argparse.ArgumentTypeError(msg)
    return ivalue


def check_port(value):
    """Check that the argument port is in the range(1024, 65535).

    Args:
        value: the value to check.

    Returns:
        (int) the integer value of the arg "value".

    Raises:
        argparse.ArgumentTypeError if check fails.
    """
    ivalue = int(value)
    if 1024 <= ivalue <= 65535:
        pass
    else:
        msg = "port (%s) invalid must in the range(1024, 65535)" % value
        raise argparse.ArgumentTypeError(msg)
    return ivalue


def parse_args():
    """Parse the command line arguments.

    Returns:
        args (<argparse.Namespace>): parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--router",
        default=DEFAULT_ROUTER,
        help="router name to query (default: %(default)s)"
    )
    parser.add_argument(
        "--port",
        type=check_port,
        default=DEFAULT_PORT,
        help="router SNMP port (default: %(default)s)"
    )
    parser.add_argument(
        "--interval",
        type=check_interval,
        default=DEFAULT_INTERVAL,
        help="polling interval seconds, positive integer (default: %(default)s)"
    )
    parser.add_argument(
        "--community",
        default=DEFAULT_COMMUNITY,
        help="SNMP community string (default: %(default)s)"
    )
    parser.add_argument(
        "--iterations",
        type=check_iterations,
        default=DEFAULT_ITERATIONS,
        help="Number of polls to execute, positive integer or 0 (forever) (default: %(default)s)"
    )
    return parser.parse_args()


def poll(args):
    """Poll the two router interfaces for input and output byte counts.

    Polling continues forever if the iterations argument is 0.

    Display sthe bytes/second line rate and the total input/output byte counts for each
    interface. The first display will occur at 2x the polling interval as the first poll
    initializes the "last" dictionary values.

    Args:
        args (<argparse.Namespace>): parsed command line arguments.

    Returns:
        (int) ERROR or NOERROR.
    """
    ifname = {
        OID_IFHCINOCTETS + OID_IF1: 'eth0 input',
        OID_IFHCINOCTETS + OID_IF2: 'eth1 input',
        OID_IFHCOUTOCTETS + OID_IF1: 'eth0 output',
        OID_IFHCOUTOCTETS + OID_IF2: 'eth1 output'
    }
    last = {
        OID_IFHCINOCTETS + OID_IF1: 0,
        OID_IFHCINOCTETS + OID_IF2: 0,
        OID_IFHCOUTOCTETS + OID_IF1: 0,
        OID_IFHCOUTOCTETS + OID_IF2: 0
    }
    loop_cnt = -1
    retval = NOERROR
    command = cmdgen.CommandGenerator()
    while loop_cnt < args.iterations:
        error_indication, error_status, error_index, var_binds = command.getCmd(
            cmdgen.CommunityData(args.community),
            cmdgen.UdpTransportTarget((args.router, args.port)),
            OID_IFHCINOCTETS + OID_IF1,
            OID_IFHCINOCTETS + OID_IF2,
            OID_IFHCOUTOCTETS + OID_IF1,
            OID_IFHCOUTOCTETS + OID_IF2
        )
        if error_indication:
            print(error_indication)
        else:
            if error_status:
                print('%s at %s' % (error_status,
                                    error_index and var_binds[int(error_index) - 1] or '?'))
                retval = ERROR
            else:
                for name, val in var_binds:
                    current = val - last[str(name)]
                    rate = int(current / args.interval)
                    if last[str(name)] > 0:
                        print('%s: %s bytes/sec %s total bytes' % (ifname[str(name)], rate, val))
                    last[str(name)] = val
                print('')
        time.sleep(args.interval)
        if args.iterations > 0:
            loop_cnt += 1
    return retval


def main():
    """Parse the command line arguments and start the polling.

    Returns:
        (int) ERROR or NOERROR.
    """
    args = parse_args()
    return poll(args)


if __name__ == "__main__":
    main()
