#!/usr/bin/env python3
#

"""
get RRset, given zoneid, qname, and qtype.
"""

import sys
from botocore.exceptions import ClientError
from r53utils import get_client, get_rrset, rrset_to_text, R53Error


if __name__ == '__main__':

    zoneid, qname, qtype = sys.argv[1:]
    if not qname.endswith('.'):
        qname += "."

    client = get_client()
    try:
        rrset = get_rrset(client, zoneid, qname, qtype)
    except (R53Error, ClientError) as error:
        print("Error: {}".format(error))
    else:
        print(rrset_to_text(rrset))
