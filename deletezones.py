#!/usr/bin/env python3
#

"""
Delete all Route53 zones given on the command line by name.

Obtains a list of all Route53 zones, obtains the zoneid of any
zone whose name matches one of the given names, then deletes that
zone. Before deleting the zone, it inspects all RRsets within the
zone and deletes all of them except the zone apex NS and SOA - a
pre-requisite to Route53's zone deletion operation.

"""

import sys
import r53utils


def delete_zone(r53client, zone, zoneid):
    """Delete zone identified by given zoneid"""
    r53utils.empty_zone(r53client, zoneid, zonename=zone)
    r53utils.delete_zone(r53client, zoneid)
    print("DELETED zone: {} {}".format(zone, zoneid))
    return


if __name__ == '__main__':

    ZONES = []
    for zonename in sys.argv[1:]:
        if not zonename.endswith('.'):
            zonename += "."
        ZONES.append(zonename)

    client = r53utils.get_client()
    for zone in r53utils.generator_hosted_zones(client):
        if zone['Name'] in ZONES:
            delete_zone(client, zone['Name'], zone['Id'])
