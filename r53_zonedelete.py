#!/usr/bin/env python3
#

import os, sys, boto3, pprint, random


if __name__ == '__main__':

    caller_ref = "shuque.{:05d}".format(random.randint(1,10000))
    print(caller_ref)
    client = boto3.client('route53')
    zoneid = sys.argv[1]

    print("Deleting zone with id: {}".format(zoneid))

    response = client.delete_hosted_zone(Id=zoneid)
    pprint.pprint(response)
