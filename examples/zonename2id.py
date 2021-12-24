#!/usr/bin/env python3
#

"""
Print zoneid from given zone name.
"""

import sys
from r53utils import get_client, name_to_zoneid


if __name__ == '__main__':

    zonename, = sys.argv[1:]
    if not zonename.endswith('.'):
        zonename += "."
    client = get_client()
    print(name_to_zoneid(client, zonename))
