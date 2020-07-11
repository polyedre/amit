#!/usr/bin/env python3

# List of fields known. Do not put these lines in verbose level 1
LDAP_UNINTERESTING_FIELDS = [
    "accountExpires",
    "badPasswordTime",
    "badPwdCount",
    "codePage",
    "countryCode",
    "dSCorePropagationData",
    "description",
    "displayName",
    "distinguishedName",
    "dn",
    "groupType",
    "instanceType",
    "lastLogoff",
    "lastLogon",
    "lastLogonTimestamp",
    "localPolicyFlags",
    "logonCount",
    "member",
    "memberOf",
    "msDFSR-ComputerReferenceBL",
    "msDS-SupportedEncryptionTypes",
    "objectCategory",
    "objectClass",
    "objectGUID",
    "objectSid",
    "primaryGroupID",
    "pwdLastSet",
    "rIDSetReferences",
    "sAMAccountType",
    "serverReferenceBL",
    "servicePrincipalName",
    "showInAdvancedViewOnly",
    "uSNChanged",
    "uSNCreated",
    "userAccountControl",
    "whenChanged",
    "whenCreated",
    "cn",
    "sn",
    "givenName",
    "name",
]

LDAP_POTENTIAL_USERNAME_FIELDS = [
    "sAMAccountName",
    "userPrincipalName",
]


SMB_SCAN_COMMANDS = {
    "enumdomains",
    "enumdomusers",
    "enumdomgroups",
    "enumalsgroups domain",
    "enumalsgroups builtin",
}
