#!/usr/bin/env python3
#

"""
Given a Route53 zoneid, print all the resource record sets in the zone.

"""

import sys
import pprint
import json
import botocore
from r53utils import get_client, generator_rrsets


if __name__ == '__main__':

    client = get_client()
    zoneid = sys.argv[1]

    rrset_list = []
    try:
        for rrset in generator_rrsets(client, zoneid):
            rrset_list.append(rrset)
    except botocore.exceptions.ClientError as err:
        print("ERROR:", err)
    else:
        print(json.dumps(rrset_list))
