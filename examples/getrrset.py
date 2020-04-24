#!/usr/bin/env python3
#

import sys
from r53utils import get_client, get_rrset, rrset_to_text


if __name__ == '__main__':

    zoneid, qname, qtype = sys.argv[1:]
    if not qname.endswith('.'):
        qname += "."

    client = get_client()
    try:
        rrset = get_rrset(client, zoneid, qname, qtype)
    except Exception as e:
        print("Error: {}".format(e))
    else:
        print(rrset_to_text(rrset))
