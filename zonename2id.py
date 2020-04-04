#!/usr/bin/env python3
#

import sys
import r53utils


if __name__ == '__main__':

    zonename, = sys.argv[1:]
    if not zonename.endswith('.'):
        zonename += "."
    client = r53utils.get_client()
    print(r53utils.name_to_zoneid(client, zonename))

