#!/usr/bin/env python3
#

import os, sys, boto3, pprint, random


if __name__ == '__main__':

    caller_ref = "shuque.{:05d}".format(random.randint(1,10000))
    print(caller_ref)
    client = boto3.client('route53')
    zone = sys.argv[1]

    print("Creating zone: {}".format(zone))

    response = client.create_hosted_zone(
        Name=zone,
        CallerReference=caller_ref)
    pprint.pprint(response)
    print('')

    rmd = response['ResponseMetadata']
    if rmd['HTTPStatusCode'] != 201:
        print("FAIL")
    else:
        print("OK")
        hostedzone = response['HostedZone']
        print("Zone: {}".format(hostedzone['Name']))
        print("Id: {}".format(hostedzone['Id']))
        nsset = response['DelegationSet']['NameServers']
        for ns in nsset:
            print("Nameserver: {}".format(ns))


