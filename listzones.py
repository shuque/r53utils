#!/usr/bin/env python3
#

"""
Print all hosted Route53 zones in the current account.

"""

import r53utils


if __name__ == '__main__':

    client = r53utils.get_client()
    for zone in r53utils.generator_hosted_zones(client):
        print("{} {} {} {}".format(
            zone['Name'],
            zone['Id'],
            "private" if zone['Config']['PrivateZone'] else "public",
            zone['ResourceRecordSetCount']))
