#!/usr/bin/env python3

import json


class DomainEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Domain):
            return {o.name: [ip for ip in o.ips]}
        return json.JSONEncoder.default(self, o)


class Domain:
    def __init__(self, name, ips=set()):
        self.name = name
        self.ips = set(ips)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return f"{self.name:50} {', '.join(self.ips)}"

    def __hash__(self):
        return hash(self.name)


class HostEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Host):
            return {
                o.ip: {
                    "services": [ServiceEncoder().default(s) for s in o.services],
                    "domains": [d.name for d in o.domains],
                }
            }
        return json.JSONEncoder.default(self, o)


class Host:
    def __init__(self, ip, domains=[], services=[]):
        self.ip = ip
        self.services = set(services)
        self.domains = set(domains)

    def add_service(self, *args):
        self.services.append(Service(*args))

    def __eq__(self, other):
        return self.ip == other.ip

    def __str__(self):
        return "{:16} \n\t{}".format(
            self.ip, "\n\t".join([str(s) for s in self.services])
        )

    def __repr__(self):
        return self.ip

    def __hash__(self):
        return hash(self.ip)


class ServiceEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Service):
            return {
                "port": o.port,
                "name": o.name,
                "product": o.product,
                "version": o.version,
                "infos": o.info,
            }
        return json.JSONEncoder.default(self, o)


unknown_products = ["", "None", " None", "None "]


class Service:
    def __init__(self, port, name="", product="", version=""):
        self.port = int(port)
        self.name = name
        self.product = product
        self.version = version
        self.info = dict()

    def __str__(self):
        return f"{self.port:<6}{self.name:15} {self.product} {self.version}"

    def __hash__(self):
        return hash(self.port)

    def merge(self, service):
        # Version
        if self.version != service.version:
            if self.version == "None":
                self.version = service.version
            else:
                self.version = f"{self.version}, {service.version}"

        # Product
        if self.product != service.product and service.product not in unknown_products:
            if self.product in unknown_products:
                self.product = service.product
            else:
                self.product = f"{self.product}, {service.product}"

        # Info
        self.info.update(service.info)

    def __eq__(self, o):
        return isinstance(o, Service) and self.port == o.port


class ManagerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Manager):
            return {
                "domains": [DomainEncoder().default(d) for d in o.domains],
                "hosts": [HostEncoder().default(m) for m in o.hosts],
            }
        else:
            print("Not recognized : ", o, type(o))
        return json.JSONEncoder.default(self, o)


class Manager(json.JSONEncoder):
    def __init__(self):
        super().__init__()
        self.jobs = []
        self.domains = set()
        self.hosts = set()

    def default(self, o):
        return [o.domains, o.hosts]

    def add_domain(self, name, ips=[]):
        domain = Domain(name, ips)
        if domain in self.domains:
            # Only add ips if required
            mdomain = self.get_domain_by_name(name)
            mdomain.ips = mdomain.ips.union(ips)
            return mdomain
        else:
            # Add the domain
            self.domains.add(domain)
            return domain

    def remove_domain(self, name):
        domain = Domain(name)
        return self.domains.remove(domain)

    def add_job(self, job):
        self.jobs.append(job)

    def add_host(self, ip, domains=[], services=[]):
        host = Host(ip, domains, services)
        if host in self.hosts:
            # Only add ips if required
            mhost = self.get_host_by_ip(ip)
            mhost.domains = mhost.domains.union(domains)
            for service in services:
                host_services = list(mhost.services)
                if service in host_services:
                    mservice_index = host_services.index(service)
                    mservice = host_services[mservice_index]
                    mservice.merge(service)
                else:
                    mhost.services.add(service)
            return mhost
        else:
            # Add the domain
            self.hosts.add(host)
            return host

    def remove_host(self, ip):
        host = Host(ip)
        if host in self.hosts:
            self.hosts.remove(host)
        else:
            print("ERROR: remove_host: host {} not found".format(ip))

    def get_domain_by_name(self, name):
        domains = [d for d in self.domains if d.name == name]
        if domains:
            return domains[0]
        return None

    def hosts_from_targets(self, targets):
        return [
            h
            for h in self.hosts
            for target in targets
            if h.ip == target or Domain(target) in h.domains
        ]

    def get_host_by_ip(self, ip):
        hosts = [m for m in self.hosts if m.ip == ip]
        if hosts:
            return hosts[0]
        return None

    def __str__(self):
        return "Manager"

    def __repr__(self):
        return "Manager"
