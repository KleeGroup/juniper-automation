> Required junos/python3

## Create / Update Objects
### Running directly from the git version

Add the following to your configuration :
```
set system scripts op allow-url-for-python
set system scripts language python3
```
Run the following command from the operationnal mode :
```
op url https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/op-scripts/O365-Routes.py
op url https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/op-scripts/O365-Routes.py firstarg firstargvalue
```

### Running from a local copy

Copy the file in the following location of your SRX : /var/db/scripts/op/

Add the following to your configuration :
```
set system scripts op file O365-Routes.py
set system scripts language python3
```

Run the following command from the operationnal mode :
```
op O365-Routes.py
op O365-Routes.py firstarg firstargvalue
```

### Supported Args

General Options :
- debug: enable debug output

Junos Options :
- config_group_name: junos configuration group name (default value : O365)
- routing_table: junos routing table where to put routes (default: inet.0, eg myroutingtable.inet.0 or <*>.inet.0)
- route_target: (Mandatory) junos route destination in xml (default: empty, eg "<next-hop>192.168.0.10</next-hop>")

O365 Options : (see [http://aka.ms/ipurlws](http://aka.ms/ipurlws))
- tenantname: o365 tenant name (optionnal)
- serviceareas: o365 service area (optionnal: Common | Exchange | SharePoint | Skype)
- instance: o365 instance (default: Worldwide, Worldwide | China | Germany | USGovDoD | USGovGCCHigh)

## To use routes

E.g. to use it on the default routing table :
```
set routing-options static apply-groups O365
```

to use it on the myroutingtable routing table :
```
 set routing-instances he routing-options static apply-groups O365
```
