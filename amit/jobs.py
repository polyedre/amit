#!/usr/bin/env python3

from threading import Thread
import re
from .database import (
    Machine,
    Domain,
    Job,
    add_machine,
    add_domain,
    add_service,
    add_serviceinfo,
)
from bs4 import BeautifulSoup
import subprocess
import logging
import itertools

logging.basicConfig(level=logging.DEBUG)


def port_scan(target, session):
    j = Job(name=f"port_scan({target})")
    session.add(j)
    session.commit()
    analyse_target(target, session)
    ports = nmap(target, session)
    if ports:
        nmap(target, session, options=f"-A -v -p{','.join([str(p) for p in ports])}")
    else:
        logging.warning("port_scan: no port found for target '%s'", target)
    j.status = "DONE"
    session.commit()


def nmap(target, session, options=""):
    logging.debug("started nmap on target %s with options '%s'", target, options)
    if options:
        execute(f"nmap {options} {target} -oX /tmp/{target}-nmap.xml")
    else:
        execute(f"nmap {target} -oX /tmp/{target}-nmap.xml")
    logging.debug("finished nmap on target %s with options '%s'", target, options)
    ports = []
    with open(f"/tmp/{target}-nmap.xml") as f:
        xml = BeautifulSoup("".join(f.readlines()), features="lxml")
        for machine in xml.findAll("host"):
            ip = machine.address.get("addr")
            m = add_machine(session, ip)
            for hostname in xml.findAll("hostname"):
                name = hostname.get("name")
                add_domain(session, name, machines=[m])
            for port in machine.findAll("port"):
                if port.name:
                    xml_s = port.service
                    ports.append(port.get("portid"))
                    s = add_service(
                        session,
                        port=port.get("portid"),
                        name=xml_s.get("name"),
                        machine=m,
                        product=xml_s.get("product"),
                        version=xml_s.get("version"),
                    )
                    for script in port.findAll("script"):
                        add_serviceinfo(
                            session,
                            script.get("id"),
                            script.get("output"),
                            service=s,
                            source="nmap",
                            confidence=90,
                        )
    session.commit()
    return ports


def sublist3r(target, session):
    s = session()
    j = Job(name=f"sublist3r({target})")
    s.add(j)
    s.commit()

    # Execution
    logging.debug("started sublist3r for target %s", target)
    output = execute(f"sublist3r -n -d {target}")
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
            target = execute(f"dig +short {target}").strip().split("\n")[0]
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


def execute(command):
    return subprocess.check_output(command.split(" ")).decode()


def is_ip(target):
    re_ip = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
    return re_ip.match(target)


def enum_machines(targets, session):
    for target in targets:
        Thread(target=port_scan, args=(target, session)).start()


def enum_domains(targets, session):
    for target in targets:
        Thread(target=sublist3r, args=(target, session)).start()


# def enum_domain(domain, session):
