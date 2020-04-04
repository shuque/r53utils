#!/usr/bin/env python3
#

import sys
import r53utils


if __name__ == '__main__':

    zoneid, qname, qtype = sys.argv[1:]
    if not qname.endswith('.'):
        qname += "."

    client = r53utils.get_client()
    try:
        rrset = r53utils.get_rrset(client, zoneid, qname, qtype)
    except Exception as e:
        print("Error: {}".format(e))
    else:
        print(r53utils.rrset_to_text(rrset))
