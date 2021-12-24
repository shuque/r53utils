#!/usr/bin/env python3
#

"""
Create a private zone, given zone name, AWS region, and VPC id.

    createprivzone.py foointernal.test us-east-1 vpc-024f739f0bc759f0c

"""


import os
import sys
import time
from botocore.exceptions import ClientError
from r53utils import (get_client, create_zone, wait_for_insync, R53Error)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Usage: {} <zonename> <region> <vpcid>".format(
            os.path.basename(sys.argv[0])))
        sys.exit(1)

    zonename, region, vpcid = sys.argv[1:4]

    client = get_client()
    print("Creating zone: {}".format(zonename))
    try:
        zoneid, _, caller_ref, change_info = create_zone(
            client,
            zonename,
            private=True,
            vpcinfo = (region, vpcid))
    except (R53Error, ClientError) as error:
        print("ERROR:", error)
    else:
        print("Zone created. Waiting for IN-SYNC ...")
        t0 = time.time()
        wait_for_insync(client, change_info['Id'], polltime=3)
        elapsed = time.time() - t0
        print("Time to IN-SYNC: {:.2f}s".format(elapsed))
