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
import re

arguments = {
    'debug': 'enable debug output',
    'config_group_name': 'junos configuration group name (default: O365)',
    'routing_table': 'junos routing table where to put routes (default: inet.0, eg myroutingtable.inet.0 or <*>.inet.0)',
    'route_target': '(Mandatory) junos route destination in xml (default: empty, eg "<next-hop>192.168.0.10</next-hop>")',
    'tenantname': 'o365 tenant name (optionnal)',
    'serviceareas': 'o365 service area (optionnal: Common | Exchange | SharePoint | Skype)',
    'instance': 'o365 instance (default: Worldwide, Worldwide | China | Germany | USGovDoD | USGovGCCHigh)'
}

def main():

    usage = """
        This script collect o365 ip to create static routes in O365 Group
    """
    print (usage)

    parser = argparse.ArgumentParser(description='This is a script to collect o365 ip addresses.')

    #Define the arguments accepted by parser
    # which use the key names defined in the arguments dictionary
    for key in arguments:
        parser.add_argument(('-' + key), required=False, help=arguments[key])
    args = parser.parse_args()

    # Extract the value
    debug = args.debug or None
    config_group_name = args.config_group_name or 'O365'
    routing_table = args.routing_table or 'inet.0'
    route_target = args.route_target or None
    if route_target is None:
        print('route_target argument is required - eg "<next-hop>192.168.0.10</next-hop>"');
        return
    tenantname = args.tenantname or None
    serviceareas = args.serviceareas or None
    instance = args.instance or 'Worldwide'
    routing_table_instance_name = re.search(r'(.+)\.inet\.0', routing_table) or None
    if routing_table_instance_name is not None:
        routing_table_instance_name = escape(routing_table_instance_name.group(1))
    if routing_table != 'inet.0' and routing_table_instance_name is None:
        print('routing_table wrong format - should be .*.inet.0');
        return

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
    """.format(config_group_name).strip()
    if routing_table_instance_name is not None:
        config_xml = config_xml + """
                <routing-instances>
                    <instance>
                    <name>{0}</name>
    """.format(routing_table_instance_name).strip()
    config_xml = config_xml + """
                    <routing-options>
                        <static>
    """
    i=0
    for flatIp in flatIps:
        i += 1
        config_xml = config_xml + """
                    <route>
                        <name>{0}</name>
                        {1}
                    </route>
        """.format(flatIp[1],route_target).strip()

    config_xml = config_xml + """
                        </static>
                    </routing-options>
    """
    if routing_table_instance_name is not None:
        config_xml = config_xml + """
                    </instance>
                </routing-instances>
    """
    config_xml = config_xml + """
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
