#!/usr/bin/env python3
#

import sys
import r53utils


if __name__ == '__main__':

    zoneid, qname, qtype = sys.argv[1:]
    client = r53utils.get_client()
    r53utils.test_dns_answer(client, zoneid, qname, qtype)
