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


class MachineEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Machine):
            return {
                o.ip: {
                    "services": [ServiceEncoder().default(s) for s in o.services],
                    "domains": [d.name for d in o.domains],
                }
            }
        return json.JSONEncoder.default(self, o)


class Machine:
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


class Service:
    def __init__(self, port, name, product, version):
        self.port = port
        self.name = name
        self.product = product
        self.version = version
        self.info = dict()

    def __str__(self):
        return f"{self.port:6}{self.name:15} {self.product} {self.version}"


class ManagerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Manager):
            return {
                "domains": [DomainEncoder().default(d) for d in o.domains],
                "machines": [MachineEncoder().default(m) for m in o.machines],
            }
        else:
            print("Not recognized : ", o, type(o))
        return json.JSONEncoder.default(self, o)


class Manager(json.JSONEncoder):
    def __init__(self):
        super().__init__()
        self.jobs = []
        self.domains = set()
        self.machines = set()

    def default(self, o):
        return [o.domains, o.machines]

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

    def add_machine(self, ip, domains=[], services=[]):
        machine = Machine(ip, domains, services)
        if machine in self.machines:
            # Only add ips if required
            mmachine = self.get_machine_by_ip(ip)
            mmachine.domains = mmachine.domains.union(domains)
            for service in services:
                mmachine.services.update([service])
            return mmachine
        else:
            # Add the domain
            self.machines.add(machine)
            return machine

    def remove_machine(self, ip):
        machine = Machine(ip)
        if machine in self.machines:
            self.machines.remove(machine)
        else:
            print("ERROR: remove_machine: machine {} not found".format(ip))

    def get_domain_by_name(self, name):
        domains = [d for d in self.domains if d.name == name]
        if domains:
            return domains[0]
        return None

    def get_machine_by_ip(self, ip):
        machines = [m for m in self.machines if m.ip == ip]
        if machines:
            return machines[0]
        return None

    def __str__(self):
        return "Manager"

    def __repr__(self):
        return "Manager"
