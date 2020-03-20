#!/usr/bin/env python3
#

import os, sys, boto3, pprint

# Can't be more than 100 apparently.
MAXITEMS = '100'


def print_zones(response):
    for zone in response['HostedZones']:
        print("{} {}".format(zone['Name'], zone['Id']))


if __name__ == '__main__':

    client = boto3.client('route53')

    response = client.list_hosted_zones_by_name(MaxItems=MAXITEMS)
    print_zones(response)
    
    truncated = response['IsTruncated']
    while truncated:
        response = client.list_hosted_zones_by_name(
            HostedZoneId=response['NextHostedZoneId'],
            DNSName=response['NextDNSName'],
            MaxItems=MAXITEMS)
        print_zones(response)
        truncated = response['IsTruncated']
