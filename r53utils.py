"""
Small library of routines to deal with Amazon Route53 operations.

"""

import random
import boto3


MAXITEMS = '100'
CALLER_REF_PREFIX = "r53utils"


def get_client():
    """get boto3 route53 client"""
    return boto3.client('route53')


def get_caller_ref(prefix=CALLER_REF_PREFIX):
    """return caller reference string"""
    return "{}.{:05d}".format(prefix, random.randint(1, 10000))


def status(http_response):
    """return response HTTP status code"""
    return http_response['ResponseMetadata']['HTTPStatusCode']


def generator_hosted_zones(client):
    """return generator over list of R53 hosted zones"""

    kwargs = dict(MaxItems=MAXITEMS)
    while True:
        response = client.list_hosted_zones_by_name(**kwargs)
        if status(response) != 200:
            raise Exception("list_hosted_zones_by_name() error: {}".format(
                response))
        for zone in response['HostedZones']:
            yield zone
        if response['IsTruncated']:
            kwargs['DNSName'] = response['NextDNSName']
            kwargs['HostedZoneId'] = response['NextHostedZoneId']
        else:
            break


def generator_rrsets(client, zoneid):
    """return generator over rrsets in a given R53 zoneid"""

    kwargs = dict(HostedZoneId=zoneid, MaxItems=MAXITEMS)
    while True:
        response = client.list_resource_record_sets(**kwargs)
        if status(response) != 200:
            raise Exception("list_resource_record_sets() error: {}".format(
                response))
        for rrset in response['ResourceRecordSets']:
            yield rrset
        if response['IsTruncated']:
            kwargs['StartRecordName'] = response['NextRecordName']
            kwargs['StartRecordType'] = response['NextRecordType']
        else:
            break


class ChangeBatch:
    """Class to define a Route53 ChangeBatch structure"""

    def __init__(self):
        self.data = {'Changes': []}
        return

    def create(self, rrname, rrtype, ttl, rdatalist):
        """create operation"""

        change = {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': rrname,
                'Type': rrtype,
                'TTL': ttl,
                'ResourceRecords': [{'Value': x} for x in rdatalist]
            }
        }
        self.data['Changes'].append(change)


    def delete(self, rrset):
        """delete operation"""

        change = {
            'Action': 'DELETE',
            'ResourceRecordSet': rrset
        }
        self.data['Changes'].append(change)
