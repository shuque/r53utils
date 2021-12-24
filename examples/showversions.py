#!/usr/bin/env python3
#

"""
Print versions of things.

"""

import r53utils
import boto3
import botocore


if __name__ == '__main__':

    print("boto3 version:", boto3.__version__)
    print("botocore version:", botocore.__version__)
    print("r53utils version:", r53utils.__version__)
