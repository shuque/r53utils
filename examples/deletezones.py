#!/usr/bin/env python3
#

"""
Delete all Route53 zones given on the command line by name.
"""

import sys
from botocore.exceptions import ClientError
from r53utils import (get_client, generator_zones,
                      empty_zone, delete_zone, R53Error)


if __name__ == '__main__':

    TO_DELETE = []
    for zonename in sys.argv[1:]:
        if not zonename.endswith('.'):
            zonename += "."
        TO_DELETE.append(zonename)

    client = get_client()
    for zone in generator_zones(client):
        if zone['Name'] in TO_DELETE:
            try:
                empty_zone(client, zone['Id'], zonename=zone['Name'])
                delete_zone(client, zone['Id'])
            except (R53Error, ClientError) as error:
                print("ERROR:", error)
            else:
                print("DELETED zone: {} {}".format(zone['Name'], zone['Id']))
