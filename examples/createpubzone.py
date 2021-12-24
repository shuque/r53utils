#!/usr/bin/env python3
#

"""
Create a public zone, given zone name.

    createpubzone.py foopublic.test

"""


import os
import sys
import time
import botocore
from r53utils import (get_client, create_zone, wait_for_insync,  R53Error)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Usage: {} <zonename>".format(
            os.path.basename(sys.argv[0])))
        sys.exit(1)

    zonename = sys.argv[1]

    client = get_client()
    print("Creating zone: {}".format(zonename))
    try:
        zoneid, _, caller_ref, change_info = create_zone(
            client,
            zonename)
    except (R53Error, botocore.exceptions.ClientError) as err:
        print("ERROR:", err)
    else:
        print("Zone created. Waiting for IN-SYNC ...")
        t0 = time.time()
        wait_for_insync(client, change_info['Id'], polltime=3)
        elapsed = time.time() - t0
        print("Time to IN-SYNC: {:.2f}s".format(elapsed))
