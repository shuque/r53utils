#!/usr/bin/env python3
#

"""
Delete all Route53 zones given on the command line by name.
"""

import sys
from r53utils import get_client, generator_zones, empty_zone, delete_zone


if __name__ == '__main__':

    TO_DELETE = []
    for zonename in sys.argv[1:]:
        if not zonename.endswith('.'):
            zonename += "."
        TO_DELETE.append(zonename)

    client = get_client()
    for zone in generator_zones(client):
        if zone['Name'] in TO_DELETE:
            empty_zone(client, zone['Id'], zonename=zone['Name'])
            delete_zone(client, zone['Id'])
            print("DELETED zone: {} {}".format(zone['Name'], zone['Id']))
