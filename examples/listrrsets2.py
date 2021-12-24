#!/usr/bin/env python3
#

"""
Given a Route53 zoneid, print all the resource record sets in the zone.

"""

import sys
import json
from botocore.exceptions import ClientError
from r53utils import get_client, generator_rrsets, R53Error


if __name__ == '__main__':

    client = get_client()
    zoneid = sys.argv[1]

    rrset_list = []
    try:
        for rrset in generator_rrsets(client, zoneid):
            rrset_list.append(rrset)
    except (R53Error, ClientError) as error:
        print("ERROR:", error)
    else:
        print(json.dumps(rrset_list))
