# r53utils

Help on module r53utils:

NAME
    r53utils - Small library of routines to deal with Amazon Route53 operations.

DESCRIPTION
    Author: Shumon Huque

CLASSES
    builtins.Exception(builtins.BaseException)
        R53Error
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

    class R53Error(builtins.Exception)
     |  R53Error Class
     |
     |  Method resolution order:
     |      R53Error
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |
     |  Data descriptors defined here:
     |
     |  __weakref__
     |      list of weak references to the object (if defined)
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.Exception:
     |
     |  __init__(self, /, *args, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Static methods inherited from builtins.Exception:
     |
     |  __new__(*args, **kwargs) from builtins.type
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.BaseException:
     |
     |  __delattr__(self, name, /)
     |      Implement delattr(self, name).
     |
     |  __getattribute__(self, name, /)
     |      Return getattr(self, name).
     |
     |  __reduce__(...)
     |      Helper for pickle.
     |
     |  __repr__(self, /)
     |      Return repr(self).
     |
     |  __setattr__(self, name, value, /)
     |      Implement setattr(self, name, value).
     |
     |  __setstate__(...)
     |
     |  __str__(self, /)
     |      Return str(self).
     |
     |  with_traceback(...)
     |      Exception.with_traceback(tb) --
     |      set self.__traceback__ to tb and return self.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from builtins.BaseException:
     |
     |  __cause__
     |      exception cause
     |
     |  __context__
     |      exception context
     |
     |  __dict__
     |
     |  __suppress_context__
     |
     |  __traceback__
     |
     |  args

FUNCTIONS
    change_rrsets(client, zoneid, change_batch)
        create/delete/update RRsets in a zone

    create_zone(client, zonename, private=False, vpcinfo=None)
        Create zone in Route53; private zones require vpc region and id;
        Returns: zoneid, NS set, caller_ref, and change_info.

    delete_zone(client, zoneid)
        Delete zone identified by given zoneid; return ChangeInfo

    empty_zone(client, zoneid, zonename=None)
        Delete all zone RRsets except the apex SOA and NS set

    generator_rrsets(client, zoneid, maxitems='100')
        return generator over rrsets in a given R53 zoneid

    generator_zones(client, maxitems='100')
        return generator over list of R53 hosted zones

    get_caller_ref(prefix='r53utils')
        return caller reference string

    get_client(creds=None)
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

    wait_for_insync(client, changeid, polltime=5)
        Given a changeid for a previously issued route53 operation, query
        its status until it becomes in-sync, polling every 5 seconds by
        default.
        ChangeInfo: { 'Status': 'PENDING'|'INSYNC', ... }

DATA
    CALLER_REF_PREFIX = 'r53utils'
    MAXITEMS = '100'
