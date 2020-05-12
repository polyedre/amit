#!/usr/bin/env python3


class Domain:
    def __init__(self, name, ip=None):
        self.name = name
        self.subdomains = set()
        self.ip = ip

    def add_subdomain(self, domain):
        self.subdomains.add(domain)
