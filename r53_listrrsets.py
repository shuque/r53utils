#!/usr/bin/env python3
#
# Returns at most 100 records
#

import os, sys, boto3, pprint

# Can't exceed 100
MAXITEMS = '50'


def print_rrsets(response):
    for r in response['ResourceRecordSets']:
        pprint.pprint(r)


if __name__ == '__main__':

    client = boto3.client('route53')
    zoneid = sys.argv[1]

    response = client.list_resource_record_sets(
        HostedZoneId=zoneid,
        MaxItems=MAXITEMS)
    print_rrsets(response)

    truncated = response['IsTruncated']

    while truncated:
        response = client.list_resource_record_sets(
            HostedZoneId=zoneid,
            MaxItems=MAXITEMS,
            StartRecordName=response['NextRecordName'],
            StartRecordType=response['NextRecordType'])
        print_rrsets(response)
        truncated = response['IsTruncated']
