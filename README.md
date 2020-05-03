# r53utils
Small library of routines to work with Amazon Route53 service.

```
Help on module r53utils:

NAME
    r53utils - Small library of routines to deal with Amazon Route53 operations.

CLASSES
    builtins.object
        ChangeBatch
    
    class ChangeBatch(builtins.object)
     |  Class to define a Route53 ChangeBatch structure
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  create(self, rrname, rrtype, ttl, rdatalist)
     |      create operation
     |  
     |  data(self)
     |      return ChangeBatch data
     |  
     |  delete(self, rrset)
     |      delete operation
     |  
     |  reset(self)
     |      reset changebatch
     |  
     |  upsert(self, rrname, rrtype, ttl, rdatalist)
     |      upsert operation: create, or update if already exists
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FUNCTIONS
    change_rrsets(client, zoneid, change_batch)
        create/delete/update RRsets in a zone
    
    create_zone(client, zonename, private=False, vpcinfo=None)
        Create zone in Route53; private zones require vpc region and id;
        Returns: zoneid, NS set, caller_ref, and change_info.
    
    delete_zone(client, zoneid)
        Delete zone identified by given zoneid
    
    empty_zone(client, zoneid, zonename=None)
        Delete all zone RRsets except the apex SOA and NS set
    
    generator_rrsets(client, zoneid, maxitems='100')
        return generator over rrsets in a given R53 zoneid
    
    generator_zones(client, maxitems='100')
        return generator over list of R53 hosted zones
    
    get_caller_ref(prefix='r53utils')
        return caller reference string
    
    get_client()
        get boto3 route53 client
    
    get_rrset(client, zoneid, rrname, rrtype)
        given zoneid, get specified RRset by name and type
    
    get_zone(client, zoneid)
        Get hosted zone information, given zoneid
    
    name_to_zoneid(client, zonename)
        Return zoneid for the given zone name
    
    rrset_to_text(rrset)
        Return textual presentation form of RRset
    
    status(http_response)
        return response HTTP status code
    
    test_dns_answer(client, zoneid, qname, qtype)
        test DNS answer for R53 query name and type and given zoneid

DATA
    CALLER_REF_PREFIX = 'r53utils'
    MAXITEMS = '100'

```
