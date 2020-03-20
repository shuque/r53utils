#!/usr/bin/env python3
#

"""
Given a list of DNS zones on the command line, create each zone in the
Amazon Route53 DNS service, and also setup delegation records between
all needed parent child zone pairs.
"""


import os
import sys
import pprint
import random
import boto3
import dns.name


CALLER_REF_PREFIX = "foobar"
NS_TTL = 172800


class Zone:

    def __init__(self, name, zoneid, nsset, caller_ref):
        self.name = name
        self.zoneid = zoneid
        self.nsset = nsset
        self.caller_ref = caller_ref
        return

    def info(self):
        print(self)
        print("Nameservers:")
        for ns in self.nsset:
            print("\t{}".format(ns))

    def __str__(self):
        return "<Zone: {} Id: {}>".format(self.name, self.zoneid)


class ChangeBatch:

    def __init__(self):
        self.data = { 'Changes': [] }
        return

    def create(self, rrname, rrtype, ttl, rdatalist):
        d = {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': rrname,
                'Type': rrtype,
                'TTL': ttl,
                'ResourceRecords': [{'Value': x} for x in rdatalist]
            }
        }
        self.data['Changes'].append(d)


def get_caller_ref(prefix=CALLER_REF_PREFIX):
    return "{}.{:05d}".format(prefix, random.randint(1,10000))


def create_zone(r53client, zonename):

    """Create zone in Route53"""

    caller_ref = get_caller_ref()
    response = r53client.create_hosted_zone(Name=zonename.to_text(),
                                            CallerReference=caller_ref)
    status = response['ResponseMetadata']['HTTPStatusCode']
    if status != 201:
        print("create_zone() {} failed".format(zonename.to_text()))
        return None

    return Zone(name=zonename,
                zoneid=response['HostedZone']['Id'],
                nsset=response['DelegationSet']['NameServers'],
                caller_ref=caller_ref)


def add_delegation(r53client, parent, child, ttl=NS_TTL):

    """Add delegation NS record set in parent zone to child"""

    cb = ChangeBatch()
    cb.create(child.name.to_text(), 'NS', ttl, child.nsset)

    response = r53client.change_resource_record_sets(
        HostedZoneId=parent.zoneid,
        ChangeBatch=cb.data)

    status = response['ResponseMetadata']['HTTPStatusCode']
    if status != 200:
        print("Adding child delegation failed: {}".format(child.name.to_text()))
        return False

    return True


def in_zonelist(zonename, zones):

    """
    If zonename corresponds to one of the zone objects in the zones list,
    return the zone object, else None
    """

    for zone in zones:
        if zonename == zone.name:
            return zone
    else:
        return None


def delegation_list(zones):

    """Generate list of delegations needed from zone list"""

    delegations = []

    for zone in zones:
        p = zone.name
        while p != dns.name.root:
            x = p.parent()
            parentzone = in_zonelist(x, zones)
            if parentzone is not None:
                delegations.append((zone, parentzone))
                break
            p = x

    return delegations


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: {} <zone1> <zone2> ...".format(
            os.path.basename(sys.argv[0])))
        sys.exit(1)

    client = boto3.client('route53')

    zones = []

    for zone_name in sys.argv[1:]:
        zone_name = dns.name.from_text(zone_name)
        print("Creating zone: {}".format(zone_name))
        zone = create_zone(client, zone_name)
        zones.append(zone)
        zone.info()

    for child, parent in delegation_list(zones):
        print("Creating delegation: {} -> {}".format(
            parent.name, child.name))
        if not add_delegation(client, parent, child):
            print("Failed to add delegation: {} -> {}".format(
                parent.name, child.name))
