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
import boto3


MAXITEMS = '100'


class ChangeBatch:

    """Class to define a Route53 ChangeBatch structure"""

    def __init__(self):
        self.data = {'Changes': []}
        return

    def delete(self, rrset):
        change = {
            'Action': 'DELETE',
            'ResourceRecordSet': rrset
        }
        self.data['Changes'].append(change)


def delete_rrset(r53client, zoneid, rrset):

    """Delete RRset"""

    cb = ChangeBatch()
    cb.delete(rrset)

    response = r53client.change_resource_record_sets(
        HostedZoneId=zoneid,
        ChangeBatch=cb.data)

    status = response['ResponseMetadata']['HTTPStatusCode']
    if status != 200:
        print("Delete rrset failed: {}".format(rrset))
        return False

    return True


def get_next_rrset(r53client, zoneid):
    truncated = False
    while True:
        if not truncated:
            response = r53client.list_resource_record_sets(
                HostedZoneId=zoneid,
                MaxItems=MAXITEMS)
        else:
            response = r53client.list_resource_record_sets(
                HostedZoneId=zoneid,
                MaxItems=MAXITEMS,
                StartRecordName=response['NextRecordName'],
                StartRecordType=response['NextRecordType'])

        status = response['ResponseMetadata']['HTTPStatusCode']
        if status != 200:
            print("ERROR: list_resource_record_sets() failed.")
            return

        for r in response['ResourceRecordSets']:
            yield r
        truncated = response['IsTruncated']
        if not truncated:
            break
    return


def delete_all_rrsets(r53client, zone, zoneid):

    """Delete all RRsets except apex SOA/NS (pre-req for zone deletion)"""

    for rrset in get_next_rrset(r53client, zoneid):
        if (rrset['Name'] == zone) and (rrset['Type'] in ['SOA', 'NS']):
            continue
        delete_rrset(r53client, zoneid, rrset)


def delete_zone(r53client, zone, zoneid):
    delete_all_rrsets(r53client, zone, zoneid)
    response = r53client.delete_hosted_zone(Id=zoneid)
    status = response['ResponseMetadata']['HTTPStatusCode']
    if status != 200:
        print("ERROR: zone deletion failed: {} {}".format(zone, zoneid))
    else:
        print("DELETED zone: {} {}".format(zone, zoneid))
    return


def do_zones(r53client, response, zonelist):
    for zone in response['HostedZones']:
        if zone['Name'] in zonelist:
            delete_zone(r53client, zone['Name'], zone['Id'])
    return


if __name__ == '__main__':

    ZONES = []
    for zonename in sys.argv[1:]:
        if not zonename.endswith('.'):
            zonename += "."
        ZONES.append(zonename)

    client = boto3.client('route53')

    response = client.list_hosted_zones_by_name(MaxItems=MAXITEMS)
    do_zones(client, response, ZONES)

    truncated = response['IsTruncated']
    while truncated:
        response = client.list_hosted_zones_by_name(
            HostedZoneId=response['NextHostedZoneId'],
            DNSName=response['NextDNSName'],
            MaxItems=MAXITEMS)
        do_zones(client, response, ZONES)
        truncated = response['IsTruncated']
