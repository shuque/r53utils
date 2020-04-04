#!/usr/bin/env python3
#

"""
Given a Route53 zoneid, print all the resource record sets in the zone.

"""

import sys
import pprint
import r53utils


if __name__ == '__main__':

    client = r53utils.get_client()
    zoneid = sys.argv[1]

    for rrset in r53utils.generator_rrsets(client, zoneid):
        pprint.pprint(rrset)
