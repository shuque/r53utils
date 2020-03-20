#!/usr/bin/env python3
#

"""
{'ChangeInfo': {'Id': '/change/C0803930U8ZMSM12HP49',
                'Status': 'PENDING',
                'SubmittedAt': datetime.datetime(2020, 3, 19, 0, 5, 53, 309000, tzinfo=tzutc())},
 'ResponseMetadata': {'HTTPHeaders': {'content-length': '266',
                                      'content-type': 'text/xml',
                                      'date': 'Thu, 19 Mar 2020 00:05:53 GMT',
                                      'x-amzn-requestid': 'ead29fea-0daa-4633-b709-9665f27611a6'},
                      'HTTPStatusCode': 200,
                      'RequestId': 'ead29fea-0daa-4633-b709-9665f27611a6',
                      'RetryAttempts': 0}}

"""

import os, sys, boto3, pprint, random


if __name__ == '__main__':

    caller_ref = "shuque.{:05d}".format(random.randint(1,10000))
    print(caller_ref)
    client = boto3.client('route53')
    zoneid = sys.argv[1]

    print("Deleting zone with id: {}".format(zoneid))

    response = client.delete_hosted_zone(Id=zoneid)
    pprint.pprint(response)
