Required junos/python3

Copy the file in the following location of your SRX : /cf/var/db/scripts/op/

Add the following to your configuration :
set system scripts op file O365-AddressBook.py
set system scripts language python3

Run the following command from the operationnal mode :
op O365-AddressBook.py
