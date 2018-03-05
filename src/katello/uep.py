import sys
sys.path.append('/usr/share/rhsm')
from rhsm.connection import UEPConnection

try:
    from subscription_manager import action_client
except ImportError:
    from subscription_manager import certmgr

try:
    from subscription_manager.identity import ConsumerIdentity
except ImportError:
    from subscription_manager.certlib import ConsumerIdentity

try:
    from subscription_manager.injectioninit import init_dep_injection
    init_dep_injection()
except ImportError:
    pass


def lookup_consumer_id():
    try:
        certificate = ConsumerIdentity.read()
        return certificate.getConsumerId()
    except IOError:
        return None


def get_uep():
    key = ConsumerIdentity.keypath()
    cert = ConsumerIdentity.certpath()
    uep = UEPConnection(key_file=key, cert_file=cert)
    return uep


def get_manager():
    if 'subscription_manager.action_client' in sys.modules:
        mgr = action_client.ActionClient()
    else:
        # for compatability with subscription-manager >= 1.13
        mgr = certmgr.CertManager(uep=get_uep())
    return mgr
