#!/usr/bin/env python3
#

import sys
from r53utils import get_client, test_dns_answer


if __name__ == '__main__':

    zoneid, qname, qtype = sys.argv[1:]
    client = get_client()
    test_dns_answer(client, zoneid, qname, qtype)
