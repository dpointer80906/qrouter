"""qrouter - poll-query two router interfaces via SNMP,

Print input/output line rates and total byte counts for each interface.
"""
import argparse
import time
from pysnmp.entity.rfc3413.oneliner import cmdgen

OID_IFINOCTETS = '1.3.6.1.2.1.2.2.1.10'
OID_IFOUTOCTETS = '1.3.6.1.2.1.2.2.1.16'
OID_IFHCINOCTETS = '1.3.6.1.2.1.31.1.1.1.6'
OID_IFHCOUTOCTETS = '1.3.6.1.2.1.31.1.1.1.10'
OID_IF1 = '.1'
OID_IF2 = '.2'


def parse_args():
    """Parse the command line arguments.

    Returns:
        args (<argparse.Namespace>): parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--router",
        default="demo.snmplabs.com",
        help="router name to query (default: %(default)s)"
    )
    parser.add_argument(
        "--port", type=int,
        default=1161,
        help="router SNMP port (default: %(default)s)"
    )
    parser.add_argument(
        "--interval", type=int,
        default=10,
        help="polling interval in seconds (default: %(default)s)"
    )
    parser.add_argument(
        "--community",
        default="public",
        help="SNMP community string (default: %(default)s)"
    )
    return parser.parse_args()


def poll(args):
    """Poll the two router interfaces for input and output byte counts.

    Display the bytes/second line rate and the total input/output byte counts for each
    interface. The first display will occur at 2x the polling interval as the first poll
    initializes the "last" dictionary values.

    Args:
        args (<argparse.Namespace>): parsed command line arguments.

    Returns:
        Does not return.
    """
    last = {
        OID_IFHCINOCTETS + OID_IF1: 0,
        OID_IFHCINOCTETS + OID_IF2: 0,
        OID_IFHCOUTOCTETS + OID_IF1: 0,
        OID_IFHCOUTOCTETS + OID_IF2: 0
    }
    command = cmdgen.CommandGenerator()
    while 1:
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
                                    error_index and var_binds[int(error_index)-1] or '?'))
            else:
                for name, val in var_binds:
                    current = val - last[str(name)]
                    rate = int(current / args.interval)
                    if last[str(name)] > 0:
                        print('%s bytes/sec %s total' % (rate, val))
                    last[str(name)] = val
        time.sleep(args.interval)


def main():
    """Parse the command line arguments and start the polling.

    Returns:
        poll() does not return.
    """
    args = parse_args()
    poll(args)


if __name__ == "__main__":
    main()
