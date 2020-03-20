#!/usr/bin/env python3
#

import os, sys, boto3, pprint


if __name__ == '__main__':

    client = boto3.client('route53')
    zoneid, qname, qtype = sys.argv[1:]

    response = client.test_dns_answer(
        HostedZoneId=zoneid,
        RecordName=qname,
        RecordType=qtype)
    pprint.pprint(response)

