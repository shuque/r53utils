#!/usr/bin/env python3
#

"""
Print all hosted Route53 zones in the current account.

"""

import boto3


# Can't be more than 100 apparently.
MAXITEMS = '100'


def print_zones(hostedzones_list):
    """Print zone info: name, zoneid, type, rrset count"""

    for zone in hostedzones_list:
        print("{} {} {} {}".format(
            zone['Name'],
            zone['Id'],
            "private" if zone['Config']['PrivateZone'] else "public",
            zone['ResourceRecordSetCount']))


def status(http_response):
    """return response HTTP status code"""

    return http_response['ResponseMetadata']['HTTPStatusCode']


if __name__ == '__main__':

    client = boto3.client('route53')

    kwargs = dict(MaxItems=MAXITEMS)
    while True:
        response = client.list_hosted_zones_by_name(**kwargs)
        if status(response) != 200:
            raise Exception("list_hosted_zones_by_name() error: {}".format(
                response))
        print_zones(response['HostedZones'])
        if response['IsTruncated']:
            kwargs['DNSName'] = response['NextDNSName']
            kwargs['HostedZoneId'] = response['NextHostedZoneId']
        else:
            break
