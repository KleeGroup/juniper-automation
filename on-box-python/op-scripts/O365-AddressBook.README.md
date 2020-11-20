###Required junos/python3

# Running directly from the git version

Add the following to your configuration :
```
set system scripts op allow-url-for-python
set system scripts language python3
```
Run the following command from the operationnal mode :
```
op url https://raw.githubusercontent.com/KleeGroup/juniper-automation/main/on-box-python/op-scripts/O365-AddressBook.py
```
# Running from a local copy

Copy the file in the following location of your SRX : /cf/var/db/scripts/op/

Add the following to your configuration :
```
set system scripts op file O365-AddressBook.py
set system scripts language python3
```

Run the following command from the operationnal mode :
```
op O365-AddressBook.py
```
