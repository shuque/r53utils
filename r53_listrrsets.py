#!/usr/bin/env python3
#

"""
Given a Route53 zoneid, print all the resource record sets in the zone.

"""


import sys
import pprint
import boto3


# Can't exceed 100
MAXITEMS = '50'


def print_rrsets(rrsets):
    """Print rrsets"""

    for r in rrsets:
        pprint.pprint(r)


def status(http_response):
    """return response HTTP status code"""

    return http_response['ResponseMetadata']['HTTPStatusCode']


if __name__ == '__main__':

    client = boto3.client('route53')
    zoneid = sys.argv[1]

    kwargs = dict(HostedZoneId=zoneid, MaxItems=MAXITEMS)

    while True:
        response = client.list_resource_record_sets(**kwargs)
        if status(response) != 200:
            raise Exception("list_resource_record_sets() error: {}".format(
                response))
        print_rrsets(response['ResourceRecordSets'])
        if response['IsTruncated']:
            kwargs['StartRecordName'] = response['NextRecordName']
            kwargs['StartRecordType'] = response['NextRecordType']
        else:
            break
