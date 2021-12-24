#!/usr/bin/env python3
#

"""
Given a list of DNS zones on the command line, create each zone in the
Amazon Route53 DNS service, and also setup delegation records between
all needed parent child zone pairs.
"""


import os
import sys
import dns.name
from botocore.exceptions import ClientError
from r53utils import (get_client, ChangeBatch, change_rrsets,
                      create_zone, R53Error)


NS_TTL = 86400


class Zone:

    """Zone class: name, zoneid, nameserver set"""

    def __init__(self, name, zoneid, nsset, caller_ref):
        self.name = name
        self.zoneid = zoneid
        self.nsset = nsset
        self.caller_ref = caller_ref

    def info(self):
        """Print info about the zone"""
        print(self)
        print("Nameservers:")
        for nameserver in self.nsset:
            print("\t{}".format(nameserver))

    def __str__(self):
        return "<Zone: {} Id: {}>".format(self.name, self.zoneid)


def add_delegation(r53client, parent, child, ttl=NS_TTL):
    """Add delegation NS record set in parent zone to child"""

    cbatch = ChangeBatch()
    cbatch.create(child.name.to_text(), 'NS', ttl, child.nsset)

    try:
        change_rrsets(r53client, parent.zoneid, cbatch)
    except (R53Error, ClientError) as error:
        print("Adding delegation for {} failed: {}".format(
            child.name.to_text(), error))


def in_zonelist(zonename, zonelist):

    """
    If zonename corresponds to one of the zone objects in the zones list,
    return the zone object, else None
    """

    for zone in zonelist:
        if zonename == zone.name:
            return zone
    return None


def delegation_list(zones):

    """
    Generate list of delegations needed from zone list. For each
    zone find the closest ancestor zone, if it exists in the list.
    """

    delegations = []

    for zone in zones:
        zonename = zone.name
        while zonename != dns.name.root:
            ancestorname = zonename.parent()
            parent = in_zonelist(ancestorname, zones)
            if parent is not None:
                delegations.append((parent, zone))
                break
            zonename = ancestorname

    return delegations


def main(arguments):
    """main function"""

    client = get_client()

    zones = []
    for zone_name in arguments[1:]:
        zone_name = dns.name.from_text(zone_name)
        print("Creating zone: {}".format(zone_name))
        try:
            zoneid, ns_set, caller_ref, change_info = create_zone(
                client, zone_name.to_text())
            _ = change_info
        except (R53Error, ClientError) as error:
            print("ERROR:", error)
            continue
        zone = Zone(zone_name, zoneid, ns_set, caller_ref)
        zones.append(zone)
        zone.info()

    for parentzone, childzone in delegation_list(zones):
        print("Creating delegation: {} -> {}".format(
            parentzone.name, childzone.name))
        add_delegation(client, parentzone, childzone)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: {} <zone1> <zone2> ...".format(
            os.path.basename(sys.argv[0])))
        sys.exit(1)
    main(sys.argv)
