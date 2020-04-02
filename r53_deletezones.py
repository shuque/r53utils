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
    """Delete RRset from specified zone"""

    cb = ChangeBatch()
    cb.delete(rrset)

    response = r53client.change_resource_record_sets(
        HostedZoneId=zoneid,
        ChangeBatch=cb.data)

    if status(response) != 200:
        raise Exception("Delete rrset failed: {}".format(rrset))

    return


def status(http_response):
    """return response HTTP status code"""

    return http_response['ResponseMetadata']['HTTPStatusCode']


def get_next_rrset(r53client, zoneid):
    """Get next rrset in the zone"""

    kwargs = dict(HostedZoneId=zoneid, MaxItems=MAXITEMS)
    while True:
        response = r53client.list_resource_record_sets(**kwargs)
        if status(response) != 200:
            raise Exception("ERROR: list_resource_record_sets() failed.")

        for r in response['ResourceRecordSets']:
            yield r

        if response['IsTruncated']:
            kwargs['StartRecordName'] = response['NextRecordName']
            kwargs['StartRecordType'] = response['NextRecordType']
        else:
            break


def delete_all_rrsets(r53client, zone, zoneid):
    """Delete all RRsets except apex SOA/NS (pre-req for zone deletion)"""

    for rrset in get_next_rrset(r53client, zoneid):
        if (rrset['Name'] == zone) and (rrset['Type'] in ['SOA', 'NS']):
            continue
        delete_rrset(r53client, zoneid, rrset)


def delete_zone(r53client, zone, zoneid):
    """Delete zone identified by given zoneid"""

    delete_all_rrsets(r53client, zone, zoneid)
    response = r53client.delete_hosted_zone(Id=zoneid)
    if status(response) != 200:
        raise Exception("ERROR: zone deletion failed: {} {}".format(
            zone, zoneid))
    else:
        print("DELETED zone: {} {}".format(zone, zoneid))
    return


def delete_zonelist(r53client, hostedzonelist, zones_to_delete):
    """Delete all zones in given zonelist"""

    for zone in hostedzonelist:
        if zone['Name'] in zones_to_delete:
            delete_zone(r53client, zone['Name'], zone['Id'])
    return


if __name__ == '__main__':

    ZONES = []
    for zonename in sys.argv[1:]:
        if not zonename.endswith('.'):
            zonename += "."
        ZONES.append(zonename)

    client = boto3.client('route53')

    kwargs = dict(MaxItems=MAXITEMS)
    while True:
        response = client.list_hosted_zones_by_name(**kwargs)
        delete_zonelist(client, response['HostedZones'], ZONES)
        if response['IsTruncated']:
            kwargs['HostedZoneId'] = response['NextHostedZoneId']
            kwargs['DNSName'] = response['NextDNSName']
        else:
            break
