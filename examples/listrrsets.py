#!/usr/bin/env python3
#

"""
Given a Route53 zoneid, print all the resource record sets in the zone.

"""

import sys
import pprint
from r53utils import get_client, generator_rrsets


if __name__ == '__main__':

    client = get_client()
    zoneid = sys.argv[1]

    for rrset in generator_rrsets(client, zoneid):
        pprint.pprint(rrset)
