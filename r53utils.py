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


def generator_zones(client, maxitems=MAXITEMS):
    """return generator over list of R53 hosted zones"""

    kwargs = dict(MaxItems=maxitems)
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


def generator_rrsets(client, zoneid, maxitems=MAXITEMS):
    """return generator over rrsets in a given R53 zoneid"""

    kwargs = dict(HostedZoneId=zoneid, MaxItems=maxitems)
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
        self.reset()
        return

    def reset(self):
        """reset changebatch"""
        self.datadict = {'Changes': []}

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
        self.datadict['Changes'].append(change)

    def upsert(self, rrname, rrtype, ttl, rdatalist):
        """upsert operation: create, or update if already exists"""
        change = {
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': rrname,
                'Type': rrtype,
                'TTL': ttl,
                'ResourceRecords': [{'Value': x} for x in rdatalist]
            }
        }
        self.datadict['Changes'].append(change)

    def delete(self, rrset):
        """delete operation"""
        change = {
            'Action': 'DELETE',
            'ResourceRecordSet': rrset
        }
        self.datadict['Changes'].append(change)

    def data(self):
        """return ChangeBatch data"""
        if self.datadict['Changes']:
            return self.datadict
        return None


def name_to_zoneid(client, zonename):
    """Return zoneid for the given zone name"""

    zoneid_set = []
    for zone in generator_zones(client):
        if zone['Name'] == zonename:
            zoneid_set.append(zone['Id'])
    count = len(zoneid_set)
    if count == 1:
        return zoneid_set[0]
    elif count == 0:
        raise Exception("Zone {} not found".format(zonename))
    else:
        raise Exception("Multiple zone ids found: {}".format(zoneid_set))


def get_rrset(client, zoneid, rrname, rrtype):
    """given zoneid, get specified RRset by name and type"""

    response = client.list_resource_record_sets(
        HostedZoneId=zoneid,
        StartRecordName=rrname,
        StartRecordType=rrtype,
        MaxItems='1')

    if status(response) != 200:
        raise Exception("list_resource_record_sets() error: {}".format(
            response))

    rrset0 = response['ResourceRecordSets'][0]
    if rrname == rrset0['Name'] and rrtype == rrset0['Type']:
        return rrset0
    else:
        raise Exception("RRset doesn't exist")


def rrset_to_text(rrset):
    """Return textual presentation form of RRset"""

    rr_strings = []
    for rdata_dict in rrset['ResourceRecords']:
        rdata = rdata_dict['Value']
        rr_strings.append("{} {} IN {} {}".format(rrset['Name'],
                                                  rrset['TTL'],
                                                  rrset['Type'],
                                                  rdata))
    return "\n".join(rr_strings)


def test_dns_answer(client, zoneid, qname, qtype):
    """test DNS answer for R53 query name and type and given zoneid"""

    response = client.test_dns_answer(
        HostedZoneId=zoneid,
        RecordName=qname,
        RecordType=qtype)

    if status(response) != 200:
        raise Exception("test_dns_answer() error: {}".format(
            response))

    print("Answer from: {}".format(response['Nameserver']))
    print("Protocol: {}".format(response['Protocol']))
    print('')
    for rdata in response['RecordData']:
        print("{} IN {} {}".format(response['RecordName'],
                                   response['RecordType'],
                                   rdata))


def create_zone(client, zonename, private=False, vpcinfo=None):
    """
    Create zone in Route53; private zones require vpc region and id;
    Returns: zoneid, NS set, caller_ref, and change_info.
    """

    caller_ref = get_caller_ref()
    kwargs = dict(Name=zonename, CallerReference=caller_ref)
    if private:
        kwargs['HostedZoneConfig'] = {'PrivateZone': True}
        try:
            region, vpcid = vpcinfo
        except:
            raise Exception("vpc region and id must be specified")
        kwargs['VPC'] = {'VPCRegion': region, 'VPCId': vpcid}

    response = client.create_hosted_zone(**kwargs)
    if status(response) != 201:
        raise Exception("create_zone() {} failed".format(zonename))

    return (response['HostedZone']['Id'],
            response['DelegationSet']['NameServers'],
            caller_ref,
            response['ChangeInfo'])


def change_rrsets(client, zoneid, change_batch):
    """create/delete/update RRsets in a zone"""

    response = client.change_resource_record_sets(
        HostedZoneId=zoneid,
        ChangeBatch=change_batch.data())

    if status(response) != 200:
        raise Exception("change_rrsets() failed: {}".format(response))

    return response['ChangeInfo']


def get_zone(client, zoneid):
    """Get hosted zone information, given zoneid"""

    response = client.get_hosted_zone(Id=zoneid)
    if status(response) != 200:
        raise Exception("get_hosted_zone() failed: {}".format(response))
    return response['HostedZone']


def empty_zone(client, zoneid, zonename=None):
    """Delete all zone RRsets except the apex SOA and NS set"""

    if zonename is None:
        zonename = get_zone(zoneid)['Name']

    change_batch = ChangeBatch()
    for rrset in generator_rrsets(client, zoneid):
        if (rrset['Name'] == zonename) and (rrset['Type'] in ['SOA', 'NS']):
            continue
        change_batch.delete(rrset)
    if change_batch.data() is not None:
        change_rrsets(client, zoneid, change_batch)


def delete_zone(client, zoneid):
    """Delete zone identified by given zoneid"""

    response = client.delete_hosted_zone(Id=zoneid)
    if status(response) != 200:
        raise Exception("ERROR: zone deletion failed: {}".format(zoneid))
