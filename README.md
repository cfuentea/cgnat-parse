# CGNAT Parser
This project is in development. It is essentially a Python script designed to parse Cisco and Juniper CGNAT syslog messages.


# Cisco
### Release
IOS XR 6.1 or 6.3
### Syslog for CGN
- Message needs to comply to RFC5224 format.
- Field are separated by space and non-applicable field are "-"
- `<Priority> <Version> <Time stamp> <Host name> - - <Application name (NAT44 or DSLITE)> - [Record 1][Record 2]...`

   - `[EventName <L4> <Original Source IP><Inside VRF Name> <Original Source IPv6><Translated Source IP><Original Port><Translated First Source Port><Translated Last Source port>]`
   - Example: NAT44 with Bulk-Port-Alloc
    - `1 2023 May 31 11:30:00 10.0.0.1 - - NAT44 - [UserbasedA - 192.168.1.2 VRFName - 8.8.8.1 - 22345 23001]`

# Juniper
### Release
Content pending
### Syslog for CGN
- Content pending