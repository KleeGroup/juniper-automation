from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import jcs
import sys
import argparse
import json
import tempfile
import urllib.request
import uuid
import ssl

arguments = {
    'debug': 'enable debug output',
    'config_group_name': 'junos configuration group name (default: O365)',
    'addressbook_name': 'junos addressbook name (default: <*>)',
    'objects_prefix': 'junos address objects prefix (default: O365_)',
    'object_group_name': 'junos object group name (default: Grp_O365)',
    'tenantname': 'o365 tenant name (optionnal)',
    'serviceareas': 'o365 service area (optionnal: Common | Exchange | SharePoint | Skype)',
    'instance': 'o365 instance (default: Worldwide, Worldwide | China | Germany | USGovDoD | USGovGCCHigh)'
}

def main():

    usage = """
        This script collect o365 ip to create address-book in O365 Group
    """
    print (usage)

    parser = argparse.ArgumentParser(description='This is a script to collect o365 ip addresses.')

    #Define the arguments accepted by parser
    # which use the key names defined in the arguments dictionary
    for key in arguments:
        parser.add_argument(('-' + key), required=False, help=arguments[key])
    args = parser.parse_args()

    # Extract the value
    debug = args.debug
    config_group_name = args.config_group_name or 'O365'
    addressbook_name = args.addressbook_name or '<*>'
    addressbook_name = escape(addressbook_name)
    objects_prefix = args.objects_prefix or 'O365_'
    object_group_name = args.object_group_name or 'Grp_O365'
    tenantname = args.tenantname or None
    serviceareas = args.serviceareas or None
    instance = args.instance or 'Worldwide'

    clientRequestId = str(uuid.uuid4())
    endpointSets = webApiGet('endpoints', instance, clientRequestId,tenantname,serviceareas)

    flatIps = []
    for endpointSet in endpointSets:
        if endpointSet['category'] in ('Optimize', 'Allow'):
            ips = endpointSet['ips'] if 'ips' in endpointSet else []
            category = endpointSet['category']
            # IPv4 strings have dots while IPv6 strings have colons
            ip4s = [ip for ip in ips if '.' in ip]
            tcpPorts = endpointSet['tcpPorts'] if 'tcpPorts' in endpointSet else ''
            udpPorts = endpointSet['udpPorts'] if 'udpPorts' in endpointSet else ''
            flatIps.extend([(category, ip, tcpPorts, udpPorts) for ip in ip4s])
    if debug:
        print('IPv4 Firewall IP Address Ranges')
        print(','.join(sorted(set([ip for (category, ip, tcpPorts, udpPorts) in flatIps]))))

    config_xml = """
    <configuration>
        <groups>
            <name>{0}</name>
            <security replace="replace">
                <address-book>
                    <name>{1}</name>
""".format(config_group_name,addressbook_name).strip()

    i=0
    for flatIp in flatIps:
        i += 1
        config_xml = config_xml + """
                    <address>
                        <name>{0}{1}</name>
                        <ip-prefix>{2}</ip-prefix>
                    </address>
 """.format(objects_prefix,i,flatIp[1]).strip()

    i=0 
    for flatIp in flatIps:
        i += 1
        config_xml = config_xml + """
                    <address-set>
                        <name>{0}</name>
                        <address>
                            <name>{1}{2}</name>
                        </address>
                    </address-set>
 """.format(object_group_name,objects_prefix,i).strip()
 
    config_xml = config_xml + """
                </address-book>
            </security>
        </groups>
    </configuration>
    """
    if debug:
        print(config_xml)
    
    dev = Device()
    dev.open()
    try:
        with Config(dev, mode="exclusive") as cu:
            print ("    Loading and committing configuration changes")
            cu.load(config_xml, format="xml")
            if debug:
                cu.pdiff()
            diff = cu.diff()
            if diff is not None:
                cu.commit()

    except Exception as err:
        print (err)
        dev.close()
        return

    dev.close()



# helper to call the webservice and parse the response
def webApiGet(methodName, instanceName, clientRequestId,TenantName=None,ServiceAreas=None):
    ws = "https://endpoints.office.com"
    requestPath = ws + '/' + methodName + '/' + instanceName + '?clientRequestId=' + clientRequestId
    if TenantName is not None:
        requestPath = requestPath + '&TenantName=' + TenantName
    if ServiceAreas is not None:
        requestPath = requestPath + '&ServiceAreas=' + ServiceAreas
    ssl_context = ssl._create_unverified_context()
    request = urllib.request.Request(requestPath)
    with urllib.request.urlopen(request,context=ssl_context) as response:
        return json.loads(response.read().decode())

def escape(s, quote=None):
    '''Replace special characters "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
is also translated.'''
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

if __name__ == "__main__":
    main()
