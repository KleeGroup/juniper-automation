> Requirements :
> - junos/python3
> - access to "https://endpoints.office.com" from the Junos Device

# O365-Routes Event Script

## Sample Output
```
groups {
    O365 {
        routing-options {
            static {
                route 13.107.6.152/31 next-hop 192.168.0.10;
                route 13.107.18.10/31 next-hop 192.168.0.10;
                route 13.107.128.0/22 next-hop 192.168.0.10;
                route 23.103.160.0/20 next-hop 192.168.0.10;
                [..]
            }
        }
    }
}
```

## Create / Update Objects
### Running directly from the git version

Add the following to your configuration :
```
set system scripts language python3
set event-options generate-event RefreshO365 time-interval 600
set event-options policy O365-Routes events RefreshO365
set event-options policy O365-Routes then event-script O365-Routes.py arguments firstarg firstargvalue
set event-options event-script file O365-Routes.py python-script-user <user-name>
set event-options event-script file O365-Routes.py source https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/event-scripts/O365-Routes.py
```
- Script will run every 600s (10 min)
- \<user-name\> must be a junos user account with enought permissions

### Running from a local copy

Copy the file in the following location of your SRX : /var/db/scripts/event/
```
file copy https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/event-scripts/O365-Routes.py /var/db/scripts/event/
```

Add the following to your configuration :
```
set system scripts language python3
set event-options generate-event RefreshO365 time-interval 600
set event-options policy O365-Routes events RefreshO365
set event-options policy O365-Routes then event-script O365-Routes.py arguments firstarg firstargvalue
set event-options event-script file O365-Routes.py python-script-user <user-name>
```
- Script will run every 600s (10 min)
- \<user-name\> must be a junos user account with enought permissions

### Supported Args

To set arguments, add the following to your configuration :
```
set event-options policy O365-Routes then event-script O365-Routes.py arguments firstarg firstargvalue
```

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
