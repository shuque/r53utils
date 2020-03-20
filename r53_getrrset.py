#!/usr/bin/env python3
#

import os, sys, boto3, pprint


if __name__ == '__main__':

    client = boto3.client('route53')
    zoneid, qname, qtype = sys.argv[1:]

    response = client.list_resource_record_sets(
        HostedZoneId=zoneid,
        StartRecordName=qname,
        StartRecordType=qtype,
        MaxItems='1')
    pprint.pprint(response)

    if qname == response['ResourceRecordSets'][0]['Name'] and \
       qtype == response['ResourceRecordSets'][0]['Type']:
        print("OK")
    else:
        print("FAIL: RRSET does not exist.")
