#!/usr/bin/env python3
#

"""
Print all hosted Route53 zones in the current account.

"""

from r53utils import get_client, generator_zones


if __name__ == '__main__':

    client = get_client()
    for zone in generator_zones(client):
        print("{} {} {} {}".format(
            zone['Name'],
            zone['Id'],
            "private" if zone['Config']['PrivateZone'] else "public",
            zone['ResourceRecordSetCount']))
