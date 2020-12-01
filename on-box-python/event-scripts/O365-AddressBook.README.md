> Requirements :
> - junos/python3
> - access to "https://endpoints.office.com" from the Junos Device

# O365-AddressBook Event Script

## Sample Output
```
groups {
    O365 {
        security {
            address-book {
                <*> {
                    address O365_1 13.107.6.152/31;
                    address O365_2 13.107.18.10/31;
                    address O365_3 13.107.128.0/22;
                    address O365_4 23.103.160.0/20;
                    address O365_5 40.96.0.0/13;
                    [..]
                    address-set Grp_O365 {
                        address O365_1;
                        address O365_2;
                        address O365_3;
                        address O365_4;
                        address O365_5;
                    [..]
                    }
                }
            }
        }
    }
}
```

## Create / Update O365 Objects
### Running directly from the git version

Add the following to your configuration :
```
set system scripts language python3
set event-options generate-event RefreshO365 time-interval 600
set event-options policy O365-AddressBook events RefreshO365
set event-options policy O365-AddressBook then event-script O365-AddressBook.py
set event-options event-script file O365-AddressBook.py python-script-user <user-name>
set event-options event-script file O365-AddressBook.py source https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/event-scripts/O365-AddressBook.py
```
- Script will run every 600s (10 min)
- \<user-name\> must be a junos user account with enought permissions

### Running from a local copy

Copy the file in the following location of your SRX : /var/db/scripts/event/
```
file copy https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/event-scripts/O365-AddressBook.py /var/db/scripts/event/
```

Add the following to your configuration :
```
set system scripts language python3
set event-options generate-event RefreshO365 time-interval 600
set event-options policy O365-AddressBook events RefreshO365
set event-options policy O365-AddressBook then event-script O365-AddressBook.py
set event-options event-script file O365-AddressBook.py python-script-user <user-name>
```
- Script will run every 600s (10 min)
- \<user-name\> must be a junos user account with enought permissions

### Supported Args

To set arguments, add the following to your configuration :
```
set event-options policy O365-AddressBook then event-script O365-AddressBook.py arguments firstarg firstargvalue
```

General Options :
- debug: enable debug output

Junos Options :
- config_group_name: junos configuration group name (default value : O365)
- addressbook_name: junos addressbook name (default value: <*>)
- objects_prefix: junos address objects prefix (default value: "O365_")
- object_group_name: junos object group name (default value: "Grp_O365")

O365 Options : (see [http://aka.ms/ipurlws](http://aka.ms/ipurlws))
- tenantname: o365 tenant name (optionnal)
- serviceareas: o365 service area (optionnal: Common | Exchange | SharePoint | Skype)
- instance: o365 instance (default: Worldwide, Worldwide | China | Germany | USGovDoD | USGovGCCHigh)

## To use objects

E.g. to use it on the "untrust" address-book :
```
set security address-book untrust apply-groups O365
```

To use it on a policy from lan to untrust :
```
set security policies from lan to untrust policy Allow_O365 set match destination-address Grp_O365
```