#!/usr/bin/env python3

from threading import Thread
import re
from .database import Service, Machine, Domain, Job
from bs4 import BeautifulSoup
import subprocess
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)
re_ip = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")


# class NmapJob(ExecJob):
#     def __init__(self, target, session, options=""):
#         self.target = target
#         self.session = session
#         if options:
#             command = f"nmap {options} {self.target} -oX /tmp/{self.target}-nmap.xml"
#         else:
#             command = f"nmap {self.target} -oX /tmp/{self.target}-nmap.xml"
#         logging.debug(command)
#         super().__init__(command=command)

#     def parse(self, output):
#         f = open(f"/tmp/{self.target}-nmap.xml")
#         xml = BeautifulSoup("".join(f.readlines()), features="lxml")
#         for machine in xml.findAll("machine"):
#             ip = machine.address.get("addr")
#             domains = []
#             for machinename in xml.findAll("machinename"):
#                 name = machinename.get("name")
#                 domain = self.session.add_domain(name, [ip])
#                 domains.append(domain)
#             services = []
#             for port in machine.findAll("port"):
#                 if port.name:
#                     s = port.service
#                     service = Service(
#                         port.get("portid"),
#                         s.get("name"),
#                         s.get("product"),
#                         s.get("version"),
#                     )
#                     for script in port.findAll("script"):
#                         service.info[script.get("id")] = script.get("output")
#                     services.append(service)
#             scanned_machine = self.session.add_machine(ip, domains, services)
#         f.close()
#         return scanned_machine


# class EnumMachineJob(PotentiallyAsyncJob):
#     def __init__(self, target, session):
#         super().__init__(session, is_async=True)
#         self.target = target
#         self.name = f"EnumMachine({self.target})"

#     def do(self):
#         ips, domain_names = analyse_target(self.target, self.session)
#         domains = []
#         for domain_name in domain_names:
#             domain = self.session.add_domain(domain_name, ips)
#             domains.append(domain)
#         for ip in ips:
#             self.session.add_machine(ip, domains)

#         machine = NmapJob(self.target, self.session).start()
#         ports = [s.port for s in machine.services]
#         if ports:
#             logging.info(
#                 "Starting advanced scan for target %s with ports %s", self.target, ports
#             )
#             NmapJob(
#                 self.target,
#                 self.session,
#                 options=f"-A -v -p{','.join([str(p) for p in ports])}",
#                 is_async=False,
#                 register=False,
#             ).start()

#         self.finish()


def sublist3r(target, session):
    s = session()
    j = Job(name=f"sublist3r({target})")
    s.add(j)
    s.commit()

    # Execution
    logging.debug("started sublist3r for target %s", target)
    output = execute("sublist3r", "-n", "-d", target)
    logging.debug("finished sublist3r for target %s", target)

    # Parsing
    for line in output.split("\n")[9:-1]:
        if line[:3] != "[-]":
            analyse_target(line, session)
    j.status = "DONE"
    s.commit()


def analyse_target(target, session):
    m = None
    if is_ip(target):
        m = session.query(Machine).filter(Machine.ip == target).one_or_none()
        if not m:
            m = Machine(ip=target)
            session.add(m)
    else:
        domains = []
        domains.append(target)

        while True:
            target = execute("dig", "+short", target).strip().split("\n")[0]
            if not target:
                for domain_name in domains:
                    d = (
                        session.query(Domain)
                        .filter(Domain.name == domain_name)
                        .one_or_none()
                    )
                    if not d:
                        session.add(Domain(name=domain_name))
                break
            if is_ip(target):
                m = session.query(Machine).filter(Machine.ip == target).one_or_none()

                # create new domain entry for domain name not in database
                domain_instances = []
                for domain_name in domains:
                    d = (
                        session.query(Domain)
                        .filter(Domain.name == domain_name)
                        .one_or_none()
                    )
                    if not d:
                        d = Domain(name=domain_name)
                    domain_instances.append(d)

                # No machine for these domains, adding a new one
                if not m:
                    m = Machine(ip=target, domains=domain_instances)
                    session.add(m)
                else:
                    names = [domain.name for domain in m.domains]
                    for domain in domain_instances:
                        if domain.name not in names:
                            m.domains.append(domain)
                break
            else:
                domains.append(target)
    session.commit()
    return m


def execute(*args):
    return subprocess.check_output(args).decode()


def is_ip(target):
    return re_ip.match(target)


def enum_machines(targets, session):
    for target in targets:
        pass
        # EnumMachineJob(target, session).start()


def enum_domains(targets, session):
    for target in targets:
        Thread(target=sublist3r, args=(target, session)).start()


# def enum_domain(domain, session):
