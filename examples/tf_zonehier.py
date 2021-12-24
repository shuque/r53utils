#!/usr/bin/env python3
#

"""
Given a list of DNS zones on the command line, output a Terraform
configuration file that creates each zone in the Amazon Route53 DNS
service, and also setup delegation records between all needed parent
child zone pairs.
"""


import os
import sys
import dns.name


NS_TTL = 86400


def remove_trailing_dot(dnsname):
    """Remove trailing period from domain name string"""
    if dnsname.endswith('.'):
        dnsname = dnsname[:-1]
    return dnsname


def preamble():
    """Print Terraform config file preamble"""
    print("""\

variable "region" {
  default = "us-east-1"
}

provider "aws" {
  profile = "default"
  region  = var.region
}

""")


def create_zone(zonename):
    """Output zone creation Terraform instructions"""

    zonename_text = remove_trailing_dot(zonename.to_text())
    if zonename_text.endswith('.'):
        zonename_text = zonename_text[:-1]
    resource_name = zonename_text.replace('.', '_')

    print("### Zone: {}".format(zonename_text))
    print("""\
resource "aws_route53_zone" "{}" {{
  name = "{}"
}}
""".format(resource_name, zonename_text))


def add_delegation(parent, child, ttl=NS_TTL):
    """Add delegation NS record set in parent zone to child"""

    parent_text = remove_trailing_dot(parent.to_text())
    child_text = remove_trailing_dot(child.to_text())
    parent_resource = parent_text.replace('.', '_')
    child_resource = child_text.replace('.', '_')

    print("### Delegation: {} -> {}".format(parent_text, child_text))
    print("""\
resource "aws_route53_record" "ns-{0}" {{
  zone_id = aws_route53_zone.{1}.zone_id
  name = "{2}"
  type = "NS"
  ttl = "{3}"
  records = aws_route53_zone.{4}.name_servers
}}
""".format(child_resource, parent_resource, child_text, ttl, child_resource))
    return True


def delegation_list(zones):

    """
    Generate list of delegations needed from zone list. For each
    zone find the closest ancestor zone, if it exists in the list.
    """

    delegations = []

    for zonename in zones:
        orig_zonename = zonename
        while zonename != dns.name.root:
            ancestorname = zonename.parent()
            if ancestorname in zones:
                delegations.append((ancestorname, orig_zonename))
                break
            zonename = ancestorname

    return delegations


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: {} <zone1> <zone2> ...".format(
            os.path.basename(sys.argv[0])))
        sys.exit(1)

    preamble()

    ZONELIST = []

    for zone_name in sys.argv[1:]:
        zone_name = dns.name.from_text(zone_name)
        create_zone(zone_name)
        ZONELIST.append(zone_name)

    for parentzone, childzone in delegation_list(ZONELIST):
        add_delegation(parentzone, childzone)
